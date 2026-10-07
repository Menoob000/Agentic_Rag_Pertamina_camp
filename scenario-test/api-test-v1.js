import http from 'k6/http';
import { check, sleep } from 'k6';

// Konfigurasi opsi pengetesan k6
export const options = {
    // Skenario pengetesan
    scenarios: {
        // Uji coba API dasar (kesehatan API)
        health_check: {
            executor: 'constant-vus',
            vus: 5,
            duration: '10s',
            exec: 'healthCheck',
        },
        // Uji coba simulasi unggah PDF ke RAG
        // ingest_test: {
        //     executor: 'shared-iterations',
        //     vus: 2,
        //     iterations: 5,
        //     exec: 'ingestPdfCheck',
        // }
    },
    thresholds: {
        http_req_duration: ['p(95)<2000'], // 95% request harus selesai di bawah 2 detik
        http_req_failed: ['rate<0.01'],    // Error rate harus di bawah 1%
    },
};

const BASE_URL = 'http://localhost:8000'; // Sesuaikan port dapur-ai Anda

// 1. Fungsi untuk mengetes Root Endpoint
export function healthCheck() {
    const res = http.get(`${BASE_URL}/`);
    check(res, {
        'status is 200': (r) => r.status === 200,
        'API is running': (r) => r.json('status') === 'success',
    });
    sleep(1);
}

// 2. Fungsi untuk mengetes Ingest PDF (Opsional, butuh dummy PDF)
export function ingestPdfCheck() {
    // Siapkan data dummy file PDF
    const dummyPdfContent = 'dummy pdf content for testing';
    
    const data = {
        file: http.file(dummyPdfContent, 'test-rks.pdf', 'application/pdf'),
    };

    const res = http.post(`${BASE_URL}/api/ingest-pdf`, data);
    
    check(res, {
        'status is 200': (r) => r.status === 200,
        'upload accepted': (r) => r.json('status') === 'success',
    });
    sleep(2);
}
