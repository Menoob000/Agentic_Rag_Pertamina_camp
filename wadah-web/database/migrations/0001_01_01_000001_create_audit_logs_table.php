<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     *
     * Tabel audit_logs menyimpan metadata setiap aktivitas generate RKS.
     * Sesuai SRS: "Menyimpan metadata setiap aktivitas (waktu, identitas
     * pengguna, parameter awal) ke pangkalan data relasional tanpa
     * menyimpan dokumen akhir yang bersifat sensitif."
     */
    public function up(): void
    {
        Schema::create('audit_logs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('jenis_pekerjaan');
            $table->text('detail_pekerjaan');
            $table->string('lokasi')->nullable();
            $table->string('original_filename');
            $table->enum('status', ['processing', 'success', 'failed'])->default('processing');
            $table->text('error_message')->nullable();
            $table->unsignedInteger('processing_time_ms')->nullable();
            $table->timestamps();

            // Index untuk query performa
            $table->index(['user_id', 'created_at']);
            $table->index('status');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('audit_logs');
    }
};
