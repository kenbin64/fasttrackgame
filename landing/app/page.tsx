"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import HeroSection from '@/components/HeroSection';
import LiveDemo from '@/components/LiveDemo';
import FeaturesSection from '@/components/FeaturesSection';
import PricingSection from '@/components/PricingSection';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-purple-950 to-slate-950">
      {/* Hero Section - Announces the ButterflyFx Paradigm */}
      <HeroSection />
      
      {/* Live Demo - Image Compression */}
      <LiveDemo />
      
      {/* Features */}
      <FeaturesSection />
      
      {/* Pricing */}
      <PricingSection />
    </main>
  );
}

