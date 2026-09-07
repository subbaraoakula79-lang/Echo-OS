/**
 * ECHO OS — Voice Engine
 * Browser-based voice capture, wake word detection, and TTS playback.
 */

export class VoiceEngine {
  private mediaRecorder: MediaRecorder | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private stream: MediaStream | null = null;
  private recognition: any = null; // SpeechRecognition
  private audioQueue: ArrayBuffer[] = [];
  private isPlaying = false;

  public onAudioLevel: ((level: number) => void) | null = null;
  public onTranscript: ((text: string, isFinal: boolean) => void) | null = null;
  public onWakeWord: (() => void) | null = null;

  async init() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      this.audioContext = new AudioContext();
      const source = this.audioContext.createMediaStreamSource(this.stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      source.connect(this.analyser);

      this.startLevelMonitor();
      this.initSpeechRecognition();

      return true;
    } catch (error) {
      console.error('Microphone access denied:', error);
      return false;
    }
  }

  private startLevelMonitor() {
    if (!this.analyser) return;

    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);

    const tick = () => {
      if (!this.analyser) return;
      this.analyser.getByteFrequencyData(dataArray);

      // Calculate RMS volume level (0-1)
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += (dataArray[i] / 255) ** 2;
      }
      const level = Math.sqrt(sum / dataArray.length);
      this.onAudioLevel?.(level);

      requestAnimationFrame(tick);
    };

    tick();
  }

  private initSpeechRecognition() {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';

    this.recognition.onresult = (event: any) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript;
        const isFinal = result.isFinal;

        // Wake word detection
        if (text.toLowerCase().includes('hey echo') || text.toLowerCase().includes('hey echo')) {
          this.onWakeWord?.();
        }

        this.onTranscript?.(text, isFinal);
      }
    };

    this.recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      if (event.error !== 'no-speech') {
        setTimeout(() => this.recognition?.start(), 1000);
      }
    };

    this.recognition.onend = () => {
      // Auto-restart for continuous listening
      try {
        this.recognition?.start();
      } catch {}
    };
  }

  startListening() {
    try {
      this.recognition?.start();
    } catch {}
  }

  stopListening() {
    try {
      this.recognition?.stop();
    } catch {}
  }

  getFrequencyData(): Uint8Array {
    if (!this.analyser) return new Uint8Array(0);
    const data = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(data);
    return data;
  }

  async playAudio(audioData: ArrayBuffer) {
    this.audioQueue.push(audioData);
    if (!this.isPlaying) {
      this.processAudioQueue();
    }
  }

  private async processAudioQueue() {
    if (this.audioQueue.length === 0) {
      this.isPlaying = false;
      return;
    }

    this.isPlaying = true;
    const data = this.audioQueue.shift()!;

    try {
      const ctx = new AudioContext();
      const buffer = await ctx.decodeAudioData(data);
      const source = ctx.createBufferSource();
      source.buffer = buffer;
      source.connect(ctx.destination);
      source.onended = () => this.processAudioQueue();
      source.start(0);
    } catch (error) {
      console.error('Audio playback error:', error);
      this.processAudioQueue();
    }
  }

  destroy() {
    this.recognition?.stop();
    this.stream?.getTracks().forEach((t) => t.stop());
    this.audioContext?.close();
    this.mediaRecorder = null;
    this.audioContext = null;
    this.analyser = null;
  }
}

export const voiceEngine = new VoiceEngine();
