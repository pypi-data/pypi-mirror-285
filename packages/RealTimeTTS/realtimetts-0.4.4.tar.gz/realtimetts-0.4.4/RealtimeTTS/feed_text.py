import logging

import queue
import threading
import uuid


class BufferStream:
    """
    A class for buffering and streaming data items.

    Attributes:
        items (queue.Queue): A thread-safe queue for storing data items.
        _stop_event (threading.Event): An event to signal stopping the generator.
    """
    def __init__(self):
        self.items = queue.Queue()
        self._stop_event = threading.Event()
        self.stopped = False
        self.stream_id = str(uuid.uuid4())
        print(f"*** creating new bufferstream {self.stream_id}")

    def add(self, item: str) -> None:
        """Add an item to the buffer."""
        print(f"*** add to bufferstream {self.stream_id}")
        self.items.put(item)

    def stop(self) -> None:
        """Signal to stop the buffer stream."""
        print("*** setting stop event")
        self._stop_event.set()
        print(f"*** status of self._stop_event is now: {self._stop_event.is_set()}")         

    def snapshot(self) -> list:
        """Take a snapshot of all items in the buffer without exhausting it.

        Returns:
            list: A list of all items currently in the buffer.
        """
        all_items = []
        temp_storage = []

        # Temporarily dequeue items to snapshot them.
        while not self.items.empty():
            item = self.items.get_nowait()
            all_items.append(item)
            temp_storage.append(item)

        # Re-queue the items.
        for item in temp_storage:
            self.items.put(item)

        return all_items

    def gen(self):
        """
        Generate items from the buffer, yielding them one at a time.

        Continues yielding items until the buffer is empty and stop has been signaled.
        """
        print(f"*** gen for bufferstream {self.stream_id}")
        while not self._stop_event.is_set() or not self.items.empty():
            print(f"*** queue empty: {self.items.empty()}, status of self._stop_event is now: {self._stop_event.is_set()}") 
            try:
                items = self.items.get(timeout=0.1)
                print(".", end="", flush=True)
                if items:
                    print(f"Items: [{items}]")
                yield items
            except queue.Empty:
                
                #print(f"*** queue empty, status of self._stop_event is now: {self._stop_event.is_set()}") 
                # if not self._stop_event.is_set():
                #     print(f"*** status of self._stop_event is now: {self._stop_event.is_set()}") 
                #     print("X", end="", flush=True)
                # else:
                #     print("#", end="", flush=True)
                continue

        self.stopped = True
        print("*** buffer exhausted")

class PushTextToAudioStream(TextToAudioStream):

    def __init__(self, 
                 engine: Union[BaseEngine, List[BaseEngine]],
                 log_characters: bool = False,
                 on_text_stream_start=None,
                 on_text_stream_stop=None,
                 on_audio_stream_start=None,
                 on_audio_stream_stop=None,
                 on_character=None,
                 output_device_index=None,
                 tokenizer: str = "nltk",
                 language: str = "en",
                 muted: bool = False,
                 level=logging.WARNING):

        self.text_stream = None

        super().__init__(engine, log_characters, on_text_stream_start, on_text_stream_stop, on_audio_stream_start, on_audio_stream_stop, on_character, output_device_index, tokenizer, language, muted, level)

    def push(self,
             text: str,
             fast_sentence_fragment: bool = True,
             buffer_threshold_seconds: float = 0.0,
             minimum_sentence_length: int = 10, 
             minimum_first_fragment_length : int = 10,
             log_synthesized_text = False,
             reset_generated_text: bool = True,
             output_wavfile: str = None,
             on_sentence_synthesized = None,
             on_audio_chunk = None,
             tokenizer: str = "",
             language: str = "",
             context_size: int = 12,
             muted: bool = False,
             sentence_fragment_delimiters: str = ".?!;:,\n…)]}。-",
             force_first_fragment_after_words=15):
        """
        Feeds text or an iterator to the stream and initiates playback.

        Args:
            text: Text to be fed.
            fast_sentence_fragment: Determines if sentence fragments should be quickly yielded.
            buffer_threshold_seconds: Time in seconds for the buffering threshold.
            minimum_sentence_length: The minimum number of characters a sentence must have.
            minimum_first_fragment_length: The minimum number of characters required for the first sentence fragment.
            log_synthesized_text: If True, logs the synthesized text chunks.
            reset_generated_text: If True, resets the generated text.
            output_wavfile: If set, saves the audio to the specified WAV file.
            on_sentence_synthesized: Callback function for synthesized sentences.
            on_audio_chunk: Callback function for audio chunks.
            tokenizer: Tokenizer to use for sentence splitting.
            language: Language to use for sentence splitting.
            context_size: Number of characters used to establish context for sentence boundary detection.
            muted: If True, disables audio playback via local speakers.
            sentence_fragment_delimiters: Characters considered as sentence delimiters.
            force_first_fragment_after_words: Number of words after which the first sentence fragment is forced to be yielded.
        """
        if self.text_stream is None:
            self.text_stream = BufferStream()
        
        self.text_stream.add(text)

        if not self.is_playing():
            self.feed(self.text_stream.gen())
            self.play_async(fast_sentence_fragment=fast_sentence_fragment,
                            buffer_threshold_seconds=buffer_threshold_seconds,
                            minimum_sentence_length=minimum_sentence_length,
                            minimum_first_fragment_length=minimum_first_fragment_length,
                            log_synthesized_text=log_synthesized_text,
                            reset_generated_text=reset_generated_text,
                            output_wavfile=output_wavfile,
                            on_sentence_synthesized=on_sentence_synthesized,
                            on_audio_chunk=on_audio_chunk,
                            tokenizer=tokenizer,
                            language=language,
                            context_size=context_size,
                            muted=muted,
                            sentence_fragment_delimiters=sentence_fragment_delimiters,
                            force_first_fragment_after_words=force_first_fragment_after_words)
    # if not self.is_playing():
    #         self.feed(text_stream.gen())
    #         self.play_async(
    #             # fast_sentence_fragment=fast_sentence_fragment,
    #             # minimum_sentence_length=min_sentence_length,
    #             # minimum_first_fragment_length=min_first_fragment_length,
    #             # # log_synthesized_text=True,
    #             # context_size=4,
    #             # muted=False,
    #             # sentence_fragment_delimiters=".?!;:,\n()[]{}。-“”„”—…/|《》¡¿\"",
    #             # force_first_fragment_after_words=force_first_fragment_after_words,
    #             )
        
