@extends('layouts.app')

@section('title', 'Buat Dokumen Tender')

@section('content')
<div class="page-header">
    <h1 class="page-title">Buat Dokumen Tender Baru</h1>
    <p class="page-desc">Isi formulir di bawah ini untuk menghasilkan seluruh paket Dokumen Tender secara otomatis menggunakan AI.</p>
</div>

<div class="card" id="tender-form-card">
    <form method="POST"
          action="{{ route('tender.generate') }}"
          enctype="multipart/form-data"
          id="tender-form"
          class="rks-form">
        @csrf

        {{-- Section 1: Informasi Umum --}}
        <h2 style="font-size: var(--font-size-lg); border-bottom: 2px solid var(--color-surface-alt); padding-bottom: var(--space-sm); margin-bottom: var(--space-md); color: var(--color-secondary);">
            Bagian 1: Informasi Umum
        </h2>
        
        <div class="form-group">
            <label for="nama_pengadaan" class="form-label">
                Nama Pengadaan <span class="required">*</span>
            </label>
            <input type="text" id="nama_pengadaan" name="nama_pengadaan" class="form-input" value="{{ old('nama_pengadaan') }}" placeholder="Contoh: Pengadaan Jasa Konstruksi Tangki" required>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md);">
            <div class="form-group">
                <label for="nomor_tender" class="form-label">
                    Nomor Tender <span class="required">*</span>
                </label>
                <input type="text" id="nomor_tender" name="nomor_tender" class="form-input" value="{{ old('nomor_tender', 'No.Project/DT/PND970000/2026-S7') }}" required>
            </div>
            <div class="form-group">
                <label for="tanggal" class="form-label">
                    Tanggal Dokumen <span class="required">*</span>
                </label>
                <input type="text" id="tanggal" name="tanggal" class="form-input" value="{{ old('tanggal', date('d F Y')) }}" required>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md);">
            <div class="form-group">
                <label for="metode_pemenuhan" class="form-label">
                    Metode Pemenuhan <span class="required">*</span>
                </label>
                <select id="metode_pemenuhan" name="metode_pemenuhan" class="form-input" required>
                    <option value="Tender Terbatas" {{ old('metode_pemenuhan') == 'Tender Terbatas' ? 'selected' : '' }}>Tender Terbatas</option>
                    <option value="Tender Umum" {{ old('metode_pemenuhan') == 'Tender Umum' ? 'selected' : '' }}>Tender Umum</option>
                    <option value="Penunjukan Langsung" {{ old('metode_pemenuhan') == 'Penunjukan Langsung' ? 'selected' : '' }}>Penunjukan Langsung</option>
                </select>
            </div>
            <div class="form-group">
                <label for="jenis_kontrak" class="form-label">
                    Jenis Kontrak <span class="required">*</span>
                </label>
                <select id="jenis_kontrak" name="jenis_kontrak" class="form-input" required>
                    <option value="Gabungan Harga Satuan & Lumpsum" {{ old('jenis_kontrak') == 'Gabungan Harga Satuan & Lumpsum' ? 'selected' : '' }}>Gabungan Harga Satuan & Lumpsum</option>
                    <option value="Lumpsum" {{ old('jenis_kontrak') == 'Lumpsum' ? 'selected' : '' }}>Lumpsum</option>
                    <option value="Harga Satuan" {{ old('jenis_kontrak') == 'Harga Satuan' ? 'selected' : '' }}>Harga Satuan</option>
                </select>
            </div>
        </div>

        <br>

        {{-- Section 2: Data Finansial & Teknis --}}
        <h2 style="font-size: var(--font-size-lg); border-bottom: 2px solid var(--color-surface-alt); padding-bottom: var(--space-sm); margin-bottom: var(--space-md); color: var(--color-secondary);">
            Bagian 2: Data Finansial & Teknis
        </h2>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md);">
            <div class="form-group">
                <label for="prime_cost" class="form-label">
                    Prime Cost (Rp) <span class="required">*</span>
                </label>
                <input type="number" id="prime_cost" name="prime_cost" class="form-input" value="{{ old('prime_cost', 13283434534) }}" step="1" required>
            </div>
            <div class="form-group">
                <label for="total_dengan_kr" class="form-label">
                    Total dengan K&R (Rp) <span class="required">*</span>
                </label>
                <input type="number" id="total_dengan_kr" name="total_dengan_kr" class="form-input" value="{{ old('total_dengan_kr', 14346100000) }}" step="1" required>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md);">
            <div class="form-group">
                <label for="resiko_csms" class="form-label">
                    Risiko CSMS <span class="required">*</span>
                </label>
                <select id="resiko_csms" name="resiko_csms" class="form-input" required>
                    <option value="Tinggi" {{ old('resiko_csms') == 'Tinggi' ? 'selected' : '' }}>Tinggi</option>
                    <option value="Sedang" {{ old('resiko_csms') == 'Sedang' ? 'selected' : '' }}>Sedang</option>
                    <option value="Rendah" {{ old('resiko_csms') == 'Rendah' ? 'selected' : '' }}>Rendah</option>
                </select>
            </div>
            <div class="form-group">
                <label for="tkdn_minimal" class="form-label">
                    TKDN Minimal (%) <span class="required">*</span>
                </label>
                <input type="number" id="tkdn_minimal" name="tkdn_minimal" class="form-input" value="{{ old('tkdn_minimal', 20.12) }}" step="0.01" required>
            </div>
        </div>

        <br>

        {{-- Section 3: Pejabat & Jadwal --}}
        <h2 style="font-size: var(--font-size-lg); border-bottom: 2px solid var(--color-surface-alt); padding-bottom: var(--space-sm); margin-bottom: var(--space-md); color: var(--color-secondary);">
            Bagian 3: Pejabat & Jadwal
        </h2>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md);">
            <div class="form-group">
                <label for="pejabat_procurement_nama" class="form-label">Nama Pejabat Procurement <span class="required">*</span></label>
                <input type="text" id="pejabat_procurement_nama" name="pejabat_procurement_nama" class="form-input" value="{{ old('pejabat_procurement_nama', 'Rigga Widar Atmagi') }}" required>
            </div>
            <div class="form-group">
                <label for="pejabat_procurement_jabatan" class="form-label">Jabatan Pejabat Procurement <span class="required">*</span></label>
                <input type="text" id="pejabat_procurement_jabatan" name="pejabat_procurement_jabatan" class="form-input" value="{{ old('pejabat_procurement_jabatan', 'Area Manager Procurement Kalimantan') }}" required>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md);">
            <div class="form-group">
                <label for="pejabat_berwenang" class="form-label">Pejabat Berwenang <span class="required">*</span></label>
                <input type="text" id="pejabat_berwenang" name="pejabat_berwenang" class="form-input" value="{{ old('pejabat_berwenang', 'Sr. Manager Opt. & Maint. Regional Kalimantan') }}" required>
            </div>
            <div class="form-group">
                <label for="pengawas_pekerjaan" class="form-label">Pengawas Pekerjaan <span class="required">*</span></label>
                <input type="text" id="pengawas_pekerjaan" name="pengawas_pekerjaan" class="form-input" value="{{ old('pengawas_pekerjaan', 'Region Manager RPD Regional Kalimantan') }}" required>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md);">
            <div class="form-group">
                <label for="pemasukan_mulai" class="form-label">Jadwal Pemasukan Mulai <span class="required">*</span></label>
                <input type="text" id="pemasukan_mulai" name="pemasukan_mulai" class="form-input" value="{{ old('pemasukan_mulai', 'Senin, 08 Desember 2025') }}" required>
            </div>
            <div class="form-group">
                <label for="pemasukan_selesai" class="form-label">Jadwal Pemasukan Selesai <span class="required">*</span></label>
                <input type="text" id="pemasukan_selesai" name="pemasukan_selesai" class="form-input" value="{{ old('pemasukan_selesai', 'Senin, 15 Desember 2025') }}" required>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md);">
            <div class="form-group">
                <label for="prebid_tanggal" class="form-label">Tanggal Pre-bid <span class="required">*</span></label>
                <input type="text" id="prebid_tanggal" name="prebid_tanggal" class="form-input" value="{{ old('prebid_tanggal', 'Senin, 08 Desember 2025') }}" required>
            </div>
            <div class="form-group">
                <label for="prebid_waktu" class="form-label">Waktu Pre-bid <span class="required">*</span></label>
                <input type="text" id="prebid_waktu" name="prebid_waktu" class="form-input" value="{{ old('prebid_waktu', '10.00 WITA') }}" required>
            </div>
        </div>

        <div class="form-group">
            <label for="prebid_tempat" class="form-label">Tempat Pre-bid <span class="required">*</span></label>
            <textarea id="prebid_tempat" name="prebid_tempat" class="form-input form-textarea" rows="2" required>{{ old('prebid_tempat', 'Microsoft Teams Meeting dengan link yang disampaikan melalui email Undangan Prebid Meeting') }}</textarea>
        </div>

        <br>

        {{-- File Upload --}}
        <div class="form-group">
            <label for="file" class="form-label">
                Dokumen Referensi / BOQ (PDF) <span class="required">*</span>
            </label>
            <div class="file-upload-area" id="file-upload-area">
                <input type="file" id="file" name="file" class="file-input" accept=".pdf" required>
                <div class="file-upload-content" id="file-upload-content">
                    <svg class="file-upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="17 8 12 3 7 8"/>
                        <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                    <p class="file-upload-text">Klik di sini atau seret file PDF BOQ untuk mengunggah</p>
                    <p class="file-upload-hint">Format: PDF · Maksimal: 50MB</p>
                </div>
                <div class="file-selected" id="file-selected" style="display:none">
                    <svg class="file-check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                    </svg>
                    <span class="file-name" id="file-name"></span>
                    <button type="button" class="file-remove" id="file-remove" title="Hapus file">&times;</button>
                </div>
            </div>
            @error('file')
                <span class="error-text" style="color: var(--color-danger); font-size: var(--font-size-sm); display: block; margin-top: 4px;">⚠ {{ $message }}</span>
            @enderror
        </div>

        {{-- Submit Button --}}
        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-generate" id="btn-generate">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <path d="M16 13H8"/>
                    <path d="M16 17H8"/>
                    <path d="M10 9H8"/>
                </svg>
                <span class="btn-text">Generate Dokumen Tender</span>
            </button>
            <p class="form-help" style="margin-top: 12px; text-align: center;">
                ✨ Data akan dikirim ke antrean AI (Background Job). Halaman akan langsung beralih seketika.
            </p>
        </div>
    </form>
</div>

{{-- Loading Overlay --}}
<div class="loading-overlay" id="loading-overlay" style="display:none">
    <div class="loading-card" style="max-width: 400px; text-align: center;">
        <div class="loading-spinner" style="margin: 0 auto 20px;"></div>
        <h3 class="loading-title">Menambahkan ke Antrean...</h3>
        <p class="loading-text">Mohon tunggu sebentar, sistem sedang mengamankan file Anda ke dalam antrean AI.</p>
    </div>
</div>
@endsection

@section('scripts')
<script>
    // File upload interaction
    const fileInput = document.getElementById('file');
    const uploadArea = document.getElementById('file-upload-area');
    const uploadContent = document.getElementById('file-upload-content');
    const fileSelected = document.getElementById('file-selected');
    const fileName = document.getElementById('file-name');
    const fileRemove = document.getElementById('file-remove');

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const file = this.files[0];
            fileName.textContent = file.name + ' (' + (file.size / 1024 / 1024).toFixed(1) + ' MB)';
            uploadContent.style.display = 'none';
            fileSelected.style.display = 'flex';
            uploadArea.classList.add('has-file');
        }
    });

    fileRemove.addEventListener('click', function() {
        fileInput.value = '';
        uploadContent.style.display = 'flex';
        fileSelected.style.display = 'none';
        uploadArea.classList.remove('has-file');
    });

    // Drag & drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', function() {
        this.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });

    // Form submit — show loading overlay
    const form = document.getElementById('tender-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    const btnGenerate = document.getElementById('btn-generate');

    form.addEventListener('submit', function() {
        loadingOverlay.style.display = 'flex';
        btnGenerate.disabled = true;
        btnGenerate.innerHTML = '<span class="loading-spinner" style="width: 16px; height: 16px; border-width: 2px; margin-right: 8px;"></span> Memproses...';
    });
</script>
@endsection
