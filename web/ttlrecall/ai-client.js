/**
 * TTL Recall AI Client
 * 
 * Unified interface to multiple AI providers:
 * - Text: OpenAI, Gemini, Anthropic, Local
 * - Voice: Web Speech API, ElevenLabs
 * - Images: DALL-E, Stable Diffusion, Midjourney
 * - Video: Runway, Pika, Stable Video
 * 
 * Optimized for speed and minimal memory usage.
 */

class TTLRecallAI {
    constructor(config = {}) {
        this.config = {
            apiEndpoint: config.apiEndpoint || 'https://ttlrecall.com/api',
            providers: config.providers || {
                text: 'openai',      // openai, gemini, anthropic, local
                voice: 'webspeech',  // webspeech, elevenlabs
                image: 'dalle',      // dalle, stable-diffusion, midjourney
                video: 'runway'      // runway, pika, stable-video
            },
            cache: config.cache !== false,
            streaming: config.streaming !== false
        };
        
        // Initialize cache
        this.cache = new Map();
        this.cacheHits = 0;
        this.cacheMisses = 0;
        
        // Initialize voice
        this.initVoice();
    }
    
    // =========================================================================
    // TEXT GENERATION
    // =========================================================================
    
    async generateText(prompt, options = {}) {
        const cacheKey = `text:${prompt}`;
        
        // Check cache
        if (this.config.cache && this.cache.has(cacheKey)) {
            this.cacheHits++;
            return this.cache.get(cacheKey);
        }
        
        this.cacheMisses++;
        
        // Call API
        const response = await fetch(`${this.config.apiEndpoint}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getApiKey()}`
            },
            body: JSON.stringify({
                prompt,
                provider: options.provider || this.config.providers.text,
                stream: options.stream || false,
                temperature: options.temperature || 0.7,
                max_tokens: options.maxTokens || 2000
            })
        });
        
        if (!response.ok) {
            throw new Error(`AI API error: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Cache result
        if (this.config.cache) {
            this.cache.set(cacheKey, data.response);
        }
        
        return data.response;
    }
    
    async *generateTextStream(prompt, options = {}) {
        const response = await fetch(`${this.config.apiEndpoint}/chat/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getApiKey()}`
            },
            body: JSON.stringify({
                prompt,
                provider: options.provider || this.config.providers.text,
                temperature: options.temperature || 0.7,
                max_tokens: options.maxTokens || 2000
            })
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    if (data.content) {
                        yield data.content;
                    }
                }
            }
        }
    }
    
    // =========================================================================
    // VOICE INPUT/OUTPUT
    // =========================================================================
    
    initVoice() {
        // Web Speech API for voice input
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
        }
        
        // Web Speech API for voice output
        this.synthesis = window.speechSynthesis;
    }
    
    startVoiceInput(onResult, onError) {
        if (!this.recognition) {
            onError(new Error('Voice input not supported'));
            return;
        }
        
        this.recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');
            
            const isFinal = event.results[event.results.length - 1].isFinal;
            onResult(transcript, isFinal);
        };
        
        this.recognition.onerror = (event) => {
            onError(new Error(event.error));
        };
        
        this.recognition.start();
    }
    
    stopVoiceInput() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }
    
    speak(text, options = {}) {
        if (!this.synthesis) {
            console.error('Speech synthesis not supported');
            return;
        }
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = options.rate || 1.0;
        utterance.pitch = options.pitch || 1.0;
        utterance.volume = options.volume || 1.0;
        
        // Select voice
        const voices = this.synthesis.getVoices();
        if (options.voice) {
            utterance.voice = voices.find(v => v.name === options.voice) || voices[0];
        }
        
        this.synthesis.speak(utterance);
        
        return new Promise((resolve) => {
            utterance.onend = resolve;
        });
    }
    
    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
        }
    }
    
    // =========================================================================
    // IMAGE GENERATION
    // =========================================================================
    
    async generateImage(prompt, options = {}) {
        const cacheKey = `image:${prompt}:${options.size || '1024x1024'}`;
        
        // Check cache
        if (this.config.cache && this.cache.has(cacheKey)) {
            this.cacheHits++;
            return this.cache.get(cacheKey);
        }
        
        this.cacheMisses++;
        
        const response = await fetch(`${this.config.apiEndpoint}/image/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getApiKey()}`
            },
            body: JSON.stringify({
                prompt,
                provider: options.provider || this.config.providers.image,
                size: options.size || '1024x1024',
                quality: options.quality || 'standard',
                style: options.style || 'natural'
            })
        });
        
        if (!response.ok) {
            throw new Error(`Image API error: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Cache result
        if (this.config.cache) {
            this.cache.set(cacheKey, data.url);
        }
        
        return data.url;
    }
    
    async editImage(imageUrl, prompt, options = {}) {
        const response = await fetch(`${this.config.apiEndpoint}/image/edit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getApiKey()}`
            },
            body: JSON.stringify({
                image: imageUrl,
                prompt,
                provider: options.provider || this.config.providers.image
            })
        });
        
        if (!response.ok) {
            throw new Error(`Image edit API error: ${response.statusText}`);
        }
        
        const data = await response.json();
        return data.url;
    }
    
    // =========================================================================
    // VIDEO GENERATION
    // =========================================================================
    
    async generateVideo(prompt, options = {}) {
        const response = await fetch(`${this.config.apiEndpoint}/video/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getApiKey()}`
            },
            body: JSON.stringify({
                prompt,
                provider: options.provider || this.config.providers.video,
                duration: options.duration || 5,
                fps: options.fps || 24,
                resolution: options.resolution || '1280x720'
            })
        });
        
        if (!response.ok) {
            throw new Error(`Video API error: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Return job ID for polling
        return {
            jobId: data.job_id,
            status: 'processing',
            pollUrl: `${this.config.apiEndpoint}/video/status/${data.job_id}`
        };
    }
    
    async getVideoStatus(jobId) {
        const response = await fetch(`${this.config.apiEndpoint}/video/status/${jobId}`, {
            headers: {
                'Authorization': `Bearer ${this.getApiKey()}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`Video status API error: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    async waitForVideo(jobId, onProgress) {
        while (true) {
            const status = await this.getVideoStatus(jobId);
            
            if (onProgress) {
                onProgress(status.progress || 0);
            }
            
            if (status.status === 'completed') {
                return status.url;
            }
            
            if (status.status === 'failed') {
                throw new Error(status.error || 'Video generation failed');
            }
            
            // Wait 2 seconds before polling again
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
    
    // =========================================================================
    // UTILITIES
    // =========================================================================
    
    getApiKey() {
        // In production, get from secure storage
        return localStorage.getItem('ttlrecall_api_key') || '';
    }
    
    setApiKey(key) {
        localStorage.setItem('ttlrecall_api_key', key);
    }
    
    clearCache() {
        this.cache.clear();
        this.cacheHits = 0;
        this.cacheMisses = 0;
    }
    
    getStats() {
        const hitRate = this.cacheHits / (this.cacheHits + this.cacheMisses) * 100;
        
        return {
            cacheSize: this.cache.size,
            cacheHits: this.cacheHits,
            cacheMisses: this.cacheMisses,
            hitRate: hitRate.toFixed(2) + '%',
            memoryUsage: this.estimateMemoryUsage()
        };
    }
    
    estimateMemoryUsage() {
        let bytes = 0;
        for (const [key, value] of this.cache) {
            bytes += key.length * 2; // UTF-16
            bytes += (typeof value === 'string' ? value.length * 2 : 100);
        }
        return (bytes / 1024 / 1024).toFixed(2) + ' MB';
    }
}

// Export for use in app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TTLRecallAI;
}
