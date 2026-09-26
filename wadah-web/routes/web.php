<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\RksController;
use App\Http\Controllers\AuditController;
use App\Http\Controllers\TenderController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| Web Routes — ITec-Ai Sistem RKS
|--------------------------------------------------------------------------
|
| Route utama untuk Zona Wadah (Web Application).
| Semua route dilindungi middleware 'auth' kecuali halaman login.
|
*/

// ── Authentication ──
Route::get('/login', [AuthController::class, 'showLogin'])->name('login');
Route::post('/login', [AuthController::class, 'login']);
Route::post('/logout', [AuthController::class, 'logout'])->name('logout');

// ── Protected Routes (requires authentication) ──
Route::middleware('auth')->group(function () {

    // Dashboard / Form Input RKS
    Route::get('/', [RksController::class, 'showForm'])->name('rks.form');

    // Generate RKS (kirim ke Dapur AI)
    Route::post('/generate-rks', [RksController::class, 'generate'])->name('rks.generate');

    // Dashboard / Form Input Tender
    Route::get('/tender', [TenderController::class, 'showForm'])->name('tender.form');
    Route::post('/generate-tender', [TenderController::class, 'generate'])->name('tender.generate');

    // Riwayat Generasi
    Route::get('/riwayat', [RksController::class, 'history'])->name('rks.history');

    // Audit Trail (admin only — dicek di controller)
    Route::get('/audit', [AuditController::class, 'index'])->name('audit.index');

    // Knowledge Base Management
    Route::get('/knowledge', [\App\Http\Controllers\KnowledgeController::class, 'index'])->name('knowledge.index');
    Route::post('/knowledge/upload', [\App\Http\Controllers\KnowledgeController::class, 'upload'])->name('knowledge.upload');
});
