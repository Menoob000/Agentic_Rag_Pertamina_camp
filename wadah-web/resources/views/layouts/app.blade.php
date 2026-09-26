<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Sistem AI Pembuat Dokumen RKS Tender - PT Pertamina Patra Niaga">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'ITec-Ai — Sistem RKS') | Pertamina</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
</head>
<body>
    {{-- ═══ NAVIGATION BAR ═══ --}}
    <nav class="navbar" id="main-navbar">
        <div class="navbar-container">
            <a href="{{ route('rks.form') }}" class="navbar-brand">
                <div class="brand-icon">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                        <rect width="32" height="32" rx="8" fill="#C41E3A"/>
                        <path d="M8 10h16v2H8zm0 5h12v2H8zm0 5h14v2H8z" fill="white"/>
                    </svg>
                </div>
                <div class="brand-text">
                    <span class="brand-name">ITec-Ai</span>
                    <span class="brand-subtitle">Sistem RKS</span>
                </div>
            </a>

            <div class="navbar-menu">
                <a href="{{ route('rks.form') }}"
                   class="nav-link {{ request()->routeIs('rks.form') ? 'active' : '' }}"
                   id="nav-form">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                        <polyline points="10 9 9 9 8 9"/>
                    </svg>
                    Buat RKS
                </a>

                <a href="{{ route('tender.form') }}"
                   class="nav-link {{ request()->routeIs('tender.*') ? 'active' : '' }}"
                   id="nav-tender">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <path d="M12 18v-6"/>
                        <path d="M8 15h8"/>
                    </svg>
                    Buat Tender
                </a>

                <a href="{{ route('knowledge.index') }}"
                   class="nav-link {{ request()->routeIs('knowledge.*') ? 'active' : '' }}"
                   id="nav-knowledge">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
                    </svg>
                    Knowledge Base
                </a>

                <a href="{{ route('rks.history') }}"
                   class="nav-link {{ request()->routeIs('rks.history') ? 'active' : '' }}"
                   id="nav-history">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    Riwayat
                </a>

                @if(Auth::user() && Auth::user()->isAdmin())
                <a href="{{ route('audit.index') }}"
                   class="nav-link {{ request()->routeIs('audit.index') ? 'active' : '' }}"
                   id="nav-audit">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                    Audit Trail
                </a>
                @endif
            </div>

            <div class="navbar-user">
                <div class="user-info">
                    <span class="user-name">{{ Auth::user()->name ?? 'Pengguna' }}</span>
                    <span class="user-role">{{ ucfirst(Auth::user()->role ?? 'ppk') }}</span>
                </div>
                <form method="POST" action="{{ route('logout') }}" class="logout-form">
                    @csrf
                    <button type="submit" class="btn-logout" id="btn-logout" title="Keluar dari sistem">
                        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                            <polyline points="16 17 21 12 16 7"/>
                            <line x1="21" y1="12" x2="9" y2="12"/>
                        </svg>
                        Keluar
                    </button>
                </form>
            </div>
        </div>
    </nav>

    {{-- ═══ MAIN CONTENT ═══ --}}
    <main class="main-content">
        <div class="container">
            {{-- Flash Messages --}}
            @if(session('success'))
            <div class="alert alert-success" id="alert-success">
                <svg class="alert-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span>{{ session('success') }}</span>
                <button class="alert-close" onclick="this.parentElement.style.display='none'">&times;</button>
            </div>
            @endif

            @if(session('error'))
            <div class="alert alert-error" id="alert-error">
                <svg class="alert-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                <span>{{ session('error') }}</span>
                <button class="alert-close" onclick="this.parentElement.style.display='none'">&times;</button>
            </div>
            @endif

            @yield('content')
        </div>
    </main>

    {{-- ═══ FOOTER ═══ --}}
    <footer class="footer">
        <div class="container">
            <p>&copy; {{ date('Y') }} ITec-Ai — Sistem Pembuat Dokumen RKS · PT Pertamina Patra Niaga</p>
        </div>
    </footer>

    @yield('scripts')
</body>
</html>
