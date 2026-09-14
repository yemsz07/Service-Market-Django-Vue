<template>
  <div class="min-h-screen bg-[#F4F4F6] text-gray-800 font-sans flex">
    
    <!-- LEFT SIDEBAR -->
    <aside class="w-64 bg-white/70 backdrop-blur-md border-r border-gray-200/80 p-6 flex flex-col justify-between hidden md:flex">
      <div class="space-y-6">
        <!-- Profile / Brand Section -->
        <div class="flex flex-col items-center text-center space-y-3 pt-4">
          <!-- Avatar Placeholder (Kung ayaw mo pa maglagay ng profile photo) -->
          <div class="w-20 h-20 rounded-full bg-gradient-to-tr from-slate-800 to-slate-600 flex items-center justify-center text-white text-2xl font-bold shadow-md">
            SM
          </div>
          <div>
            <h2 class="font-bold text-lg text-gray-900">Your Name</h2>
            <p class="text-xs text-gray-500 font-medium">@servicemarket</p>
          </div>
          <!-- Social Icons Placeholder -->
          <div class="flex space-x-2 pt-1 text-gray-400">
            <button class="p-2 hover:bg-gray-100 rounded-full transition"><i class="fab fa-github text-sm"></i></button>
            <button class="p-2 hover:bg-gray-100 rounded-full transition"><i class="fab fa-linkedin text-sm"></i></button>
            <button class="p-2 hover:bg-gray-100 rounded-full transition"><i class="fas fa-globe text-sm"></i></button>
          </div>
        </div>

        <!-- Navigation Menu -->
        <nav class="space-y-1 text-sm font-medium pt-4">
          <a href="#" class="flex items-center space-x-3 px-4 py-2.5 rounded-xl bg-white text-blue-600 shadow-sm border border-gray-100">
            <span class="w-2 h-2 rounded-full bg-blue-600"></span>
            <span>Home</span>
          </a>
          <a href="#" class="flex items-center space-x-3 px-4 py-2.5 rounded-xl text-gray-600 hover:bg-gray-100/80 transition">
            <span>Projects</span>
          </a>
          <a href="#" class="flex items-center space-x-3 px-4 py-2.5 rounded-xl text-gray-600 hover:bg-gray-100/80 transition">
            <span>Services</span>
          </a>
          <a href="#" class="flex items-center space-x-3 px-4 py-2.5 rounded-xl text-gray-600 hover:bg-gray-100/80 transition">
            <span>Architecture & Stack</span>
          </a>
          <a href="#" class="flex items-center space-x-3 px-4 py-2.5 rounded-xl text-gray-600 hover:bg-gray-100/80 transition">
            <span>About</span>
          </a>
          <a href="#" class="flex items-center space-x-3 px-4 py-2.5 rounded-xl text-gray-600 hover:bg-gray-100/80 transition">
            <span>Contact</span>
          </a>
        </nav>
      </div>

      <!-- Bottom Mini Profile / Follow -->
      <div class="flex items-center space-x-3 p-3 bg-white rounded-2xl border border-gray-200/60 shadow-sm">
        <div class="w-8 h-8 rounded-full bg-slate-700 text-white flex items-center justify-center font-bold text-xs">
          SM
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-xs font-semibold text-gray-800 truncate">ServiceMarket</p>
          <p class="text-[10px] text-gray-400">Full-Stack Architect</p>
        </div>
      </div>
    </aside>

    <!-- MAIN CONTENT AREA -->
    <main class="flex-1 p-6 md:p-10 max-w-7xl mx-auto space-y-8 overflow-y-auto">
      
      <!-- TOP HERO SECTION -->
      <header class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 pt-2">
        <div class="space-y-2">
          <h1 class="text-3xl md:text-5xl font-extrabold text-gray-900 tracking-tight">
            Build it once. Run it forever.
          </h1>
          <p class="text-sm md:text-base text-gray-500 max-w-2xl font-normal leading-relaxed">
            High-performance backend systems, polyglot persistence, and scalable escrow architectures built to endure.
          </p>
        </div>
        <button class="bg-[#0B1528] text-white px-6 py-3 rounded-full text-sm font-medium hover:bg-slate-800 transition shadow-lg shrink-0 flex items-center gap-2">
          Get in touch ↗
        </button>
      </header>

      <!-- TECH STACK TICKER / DAILY DRIVERS -->
      <section class="bg-white/80 backdrop-blur-sm rounded-2xl p-3 border border-gray-200/80 shadow-sm flex items-center gap-4 overflow-x-auto">
        <div class="px-4 py-1 text-xs font-bold text-gray-400 uppercase tracking-wider border-r border-gray-200 shrink-0">
          Daily Drivers <br>
          <span class="text-gray-800 lowercase font-semibold">Tech I work with</span>
        </div>
        <div class="flex items-center gap-6 text-xs font-semibold text-gray-600 shrink-0">
          <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-500"></span> Django REST (DRF)</span>
          <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-blue-500"></span> Django Ninja</span>
          <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-indigo-500"></span> PostgreSQL</span>
          <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-green-500"></span> MongoDB</span>
          <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-red-500"></span> Redis / Channels</span>
          <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-400"></span> Vue 3 & Tailwind</span>
          <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-amber-500"></span> PayMongo API</span>
        </div>
      </section>

      <!-- BENTO GRID CONTAINER -->
      <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <!-- BENTO CARD 1: PROJECTS (Large Card 2-Columns wide) -->
        <div class="md:col-span-2 bg-white rounded-3xl p-6 border border-gray-200/80 shadow-sm flex flex-col justify-between hover:shadow-md transition">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-8 h-8 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center font-bold text-xs">
              ⚡
            </div>
            <div>
              <h3 class="font-bold text-gray-900 text-sm">PROJECTS</h3>
              <p class="text-xs text-gray-400">Scalable platforms, fintech, and real-time backend engines</p>
            </div>
          </div>
          
          <!-- Mockup Project Preview Card Inside Bento -->
          <div class="bg-[#F8FAFC] rounded-2xl p-6 border border-gray-100 flex flex-col md:flex-row gap-6 items-center">
            <div class="space-y-3 flex-1">
              <span class="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-blue-100 text-blue-700 rounded-md">Featured Platform</span>
              <h4 class="text-xl font-bold text-gray-800">ServiceMarket Engine</h4>
              <p class="text-xs text-gray-500 leading-relaxed">
                Hybrid REST API architecture with PayMongo Escrow, asymmetric webhooks, polyglot DB storage, and async WebSocket notifications.
              </p>
            </div>
            <div class="w-full md:w-48 h-32 bg-gradient-to-tr from-slate-900 to-slate-700 rounded-xl shadow-md p-4 flex flex-col justify-between text-white shrink-0">
              <div class="flex justify-between items-center text-[10px] opacity-75">
                <span>POSTGRES + MONGO</span>
                <span>REDIS</span>
              </div>
              <div class="font-mono text-xs font-bold text-emerald-400">
                DRF + Ninja Hybrid
              </div>
            </div>
          </div>
        </div>

        <!-- BENTO CARD 2: ABOUT / ARCHITECTURE -->
        <div class="bg-white rounded-3xl p-6 border border-gray-200/80 shadow-sm flex flex-col justify-between hover:shadow-md transition">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-8 h-8 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center font-bold text-xs">
              👤
            </div>
            <div>
              <h3 class="font-bold text-gray-900 text-sm">ABOUT ME</h3>
              <p class="text-xs text-gray-400">Systems & Backend Engineering</p>
            </div>
          </div>
          <div class="space-y-3 text-xs text-gray-600 leading-relaxed">
            <p>
              I specialize in designing high-concurrency backend systems, multi-database persistence models, and secure transactional engines.
            </p>
            <div class="pt-2 flex flex-wrap gap-2">
              <span class="px-3 py-1 bg-gray-100 rounded-full text-[11px] font-medium text-gray-700">Polyglot Persistence</span>
              <span class="px-3 py-1 bg-gray-100 rounded-full text-[11px] font-medium text-gray-700">Financial Escrow</span>
              <span class="px-3 py-1 bg-gray-100 rounded-full text-[11px] font-medium text-gray-700">Real-Time Sockets</span>
            </div>
          </div>
        </div>

        <!-- BENTO CARD 3: CREDENTIALS / TECH STACK -->
        <div class="bg-white rounded-3xl p-6 border border-gray-200/80 shadow-sm flex flex-col justify-between hover:shadow-md transition">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-8 h-8 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center font-bold text-xs">
              🛡️
            </div>
            <div>
              <h3 class="font-bold text-gray-900 text-sm">CREDENTIALS</h3>
              <p class="text-xs text-gray-400">Production-ready Standards</p>
            </div>
          </div>
          <div class="flex flex-col items-center justify-center py-4 space-y-2 text-center">
            <div class="w-16 h-16 rounded-full bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 text-2xl font-bold">
              ✓
            </div>
            <p class="font-semibold text-xs text-gray-800">Enterprise Backend Certified</p>
            <p class="text-[10px] text-gray-400">ACID Compliance & JWT Security</p>
          </div>
        </div>

        <!-- BENTO CARD 4: SERVICES OFFERED -->
        <div class="bg-white rounded-3xl p-6 border border-gray-200/80 shadow-sm flex flex-col justify-between hover:shadow-md transition">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-8 h-8 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center font-bold text-xs">
              ⚙️
            </div>
            <div>
              <h3 class="font-bold text-gray-900 text-sm">SERVICES</h3>
              <p class="text-xs text-gray-400">What I architect and build</p>
            </div>
          </div>
          <ul class="space-y-2 text-xs text-gray-600">
            <li class="flex justify-between items-center py-1 border-b border-gray-100">
              <span>Django Ninja Payment APIs</span>
              <span class="text-gray-400 font-mono text-[10px]">Fast</span>
            </li>
            <li class="flex justify-between items-center py-1 border-b border-gray-100">
              <span>Real-Time WebSocket Engine</span>
              <span class="text-gray-400 font-mono text-[10px]">Redis</span>
            </li>
            <li class="flex justify-between items-center py-1 border-b border-gray-100">
              <span>Escrow State Automation</span>
              <span class="text-gray-400 font-mono text-[10px]">FinTech</span>
            </li>
            <li class="flex justify-between items-center py-1">
              <span>Vue 3 / Tailwind Frontends</span>
              <span class="text-gray-400 font-mono text-[10px]">Modern</span>
            </li>
          </ul>
        </div>

        <!-- BENTO CARD 5: TESTIMONIALS / METRICS -->
        <div class="bg-white rounded-3xl p-6 border border-gray-200/80 shadow-sm flex flex-col justify-between hover:shadow-md transition">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-8 h-8 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center font-bold text-xs">
              💬
            </div>
            <div>
              <h3 class="font-bold text-gray-900 text-sm">SYSTEM METRICS</h3>
              <p class="text-xs text-gray-400">Reliability & Speed</p>
            </div>
          </div>
          <div class="space-y-3">
            <div class="bg-gray-50 p-3 rounded-xl border border-gray-100">
              <p class="text-[11px] font-semibold text-gray-700">Sub-millisecond WebSocket Latency</p>
              <p class="text-[10px] text-gray-400">Powered by Redis in-memory channel layer</p>
            </div>
            <div class="bg-gray-50 p-3 rounded-xl border border-gray-100">
              <p class="text-[11px] font-semibold text-gray-700">Zero Transaction Loss</p>
              <p class="text-[10px] text-gray-400">Strict PostgreSQL ACID financial state machine</p>
            </div>
          </div>
        </div>

      </section>

    </main>
  </div>
</template>

<script setup>
// Pure Tailwind Vue 3 Component
</script>