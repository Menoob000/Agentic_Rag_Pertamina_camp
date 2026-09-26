<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AuditLog extends Model
{
    /**
     * Tabel audit_logs menyimpan metadata setiap aktivitas generate RKS.
     * Sesuai SRS: "Menyimpan metadata setiap aktivitas tanpa menyimpan
     * dokumen akhir yang bersifat sensitif."
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'user_id',
        'jenis_pekerjaan',
        'detail_pekerjaan',
        'lokasi',
        'original_filename',
        'status',           // 'processing', 'success', 'failed'
        'error_message',
        'file_path',
        'processing_time_ms',
    ];

    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'processing_time_ms' => 'integer',
        ];
    }

    /**
     * Relasi: Audit log dimiliki oleh satu User.
     */
    public function user()
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Scope: Filter by status sukses.
     */
    public function scopeSuccessful($query)
    {
        return $query->where('status', 'success');
    }

    /**
     * Scope: Filter by status gagal.
     */
    public function scopeFailed($query)
    {
        return $query->where('status', 'failed');
    }
}
