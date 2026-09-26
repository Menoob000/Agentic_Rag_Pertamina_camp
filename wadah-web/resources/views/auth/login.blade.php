<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Login - Sistem AI Pembuat Dokumen RKS Tender">
    <title>Masuk — ITec-Ai Sistem RKS</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
</head>
<body class="login-page">
    <div class="login-wrapper">
        {{-- Left side — Branding --}}
        <div class="login-branding">
            <div class="branding-content">
                <div class="branding-logo">
                    <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                        <rect width="64" height="64" rx="16" fill="rgba(255,255,255,0.15)"/>
                        <path d="M16 20h32v4H16zm0 10h24v4H16zm0 10h28v4H16z" fill="white"/>
                    </svg>
                </div>
                <h1 class="branding-title">ITec-Ai</h1>
                <p class="branding-subtitle">Sistem Pembuat Dokumen RKS</p>
                <p class="branding-desc">
                    Otomatisasi penyusunan dokumen Rencana Kerja dan Syarat-syarat
                    tender dengan kecerdasan buatan untuk PT Pertamina Patra Niaga.
                </p>
                <div class="branding-features">
                    <div class="feature-item">
                        <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="22 4 12 14.01 9 11.01"/>
                        </svg>
                        <span>Generate Dokumen RKS Otomatis</span>
                    </div>
                    <div class="feature-item">
                        <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="22 4 12 14.01 9 11.01"/>
                        </svg>
                        <span>Berbasis AI & Knowledge Base</span>
                    </div>
                    <div class="feature-item">
                        <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="22 4 12 14.01 9 11.01"/>
                        </svg>
                        <span>Pencatatan Audit Lengkap</span>
                    </div>
                </div>
            </div>
        </div>

        {{-- Right side — Login Form --}}
        <div class="login-form-wrapper">
            <div class="login-form-container">
                <h2 class="login-title">Masuk ke Sistem</h2>
                <p class="login-subtitle">Silakan masukkan akun Anda untuk melanjutkan</p>

                @if($errors->any())
                <div class="alert alert-error" id="login-alert">
                    <svg class="alert-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="8" x2="12" y2="12"/>
                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                    <span>{{ $errors->first() }}</span>
                </div>
                @endif

                <form method="POST" action="{{ url('/login') }}" class="login-form" id="login-form">
                    @csrf

                    <div class="form-group">
                        <label for="email" class="form-label">Alamat Email</label>
                        <div class="input-wrapper">
                            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                                <polyline points="22,6 12,13 2,6"/>
                            </svg>
                            <input type="email"
                                   id="email"
                                   name="email"
                                   value="{{ old('email') }}"
                                   class="form-input"
                                   placeholder="contoh: ppk@itec-ai.local"
                                   required
                                   autofocus>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="password" class="form-label">Kata Sandi</label>
                        <div class="input-wrapper">
                            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                            </svg>
                            <input type="password"
                                   id="password"
                                   name="password"
                                   class="form-input"
                                   placeholder="Masukkan kata sandi"
                                   required>
                        </div>
                    </div>

                    <div class="form-group form-row">
                        <label class="checkbox-label">
                            <input type="checkbox" name="remember" id="remember" class="form-checkbox">
                            <span class="checkbox-text">Ingat saya</span>
                        </label>
                    </div>

                    <button type="submit" class="btn btn-primary btn-login" id="btn-login">
                        <span class="btn-text">Masuk</span>
                        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="9 18 15 12 9 6"/>
                        </svg>
                    </button>
                </form>

                <div class="login-footer">
                    <p class="login-footer-text">
                        &copy; {{ date('Y') }} ITec-Ai · PT Pertamina Patra Niaga
                    </p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
