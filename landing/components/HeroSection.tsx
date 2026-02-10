"use client";

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export default function HeroSection() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-blue-900/20 to-pink-900/20" />
      
      {/* Particle Effect */}
      <div className="absolute inset-0 opacity-30">
        {mounted && [...Array(50)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-purple-400 rounded-full"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            animate={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            transition={{
              duration: Math.random() * 10 + 20,
              repeat: Infinity,
              ease: "linear"
            }}
          />
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 text-center">
        {/* Logo/Brand */}
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-8"
        >
          <h1 className="text-7xl md:text-9xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 mb-4">
            DimensionOS
          </h1>
          <div className="text-xl md:text-2xl text-purple-300 font-light tracking-wider">
            The ButterflyFx Paradigm
          </div>
        </motion.div>

        {/* Main Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight"
        >
          Data Doesn't Need to Exist
          <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-yellow-400 to-orange-400">
            Until You Need It
          </span>
        </motion.h2>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-xl md:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto leading-relaxed"
        >
          Store a 5MB image in <span className="text-purple-400 font-bold">6 bytes</span>.
          <br />
          Run databases with <span className="text-blue-400 font-bold">900,000:1 compression</span>.
          <br />
          Access infinite data from <span className="text-pink-400 font-bold">mathematical expressions</span>.
        </motion.p>

        {/* Key Paradigm Points */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-5xl mx-auto"
        >
          <div className="bg-purple-900/30 backdrop-blur-lg border border-purple-500/30 rounded-2xl p-6">
            <div className="text-5xl mb-3">🦋</div>
            <h3 className="text-xl font-bold text-purple-300 mb-2">Substrates</h3>
            <p className="text-gray-400 text-sm">
              Mathematical DNA containing ALL properties in superposition
            </p>
          </div>

          <div className="bg-blue-900/30 backdrop-blur-lg border border-blue-500/30 rounded-2xl p-6">
            <div className="text-5xl mb-3">🔍</div>
            <h3 className="text-xl font-bold text-blue-300 mb-2">Lenses</h3>
            <p className="text-gray-400 text-sm">
              Extract specific truths on demand - 900,000:1 compression
            </p>
          </div>

          <div className="bg-pink-900/30 backdrop-blur-lg border border-pink-500/30 rounded-2xl p-6">
            <div className="text-5xl mb-3">🌌</div>
            <h3 className="text-xl font-bold text-pink-300 mb-2">Dimensions</h3>
            <p className="text-gray-400 text-sm">
              Russian dolls model - each dimension contains the previous
            </p>
          </div>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <a
            href="#demo"
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-lg rounded-full hover:scale-105 transition-transform shadow-2xl shadow-purple-500/50"
          >
            See Live Demo
          </a>
          <a
            href="#pricing"
            className="px-8 py-4 bg-white/10 backdrop-blur-lg border border-white/20 text-white font-bold text-lg rounded-full hover:bg-white/20 transition-all"
          >
            Start Free Trial
          </a>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1.2 }}
          className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-white/50 text-sm"
          >
            ↓ Scroll to see the magic ↓
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

