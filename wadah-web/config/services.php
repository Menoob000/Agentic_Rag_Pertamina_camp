<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Dapur AI Microservice Configuration
    |--------------------------------------------------------------------------
    |
    | Konfigurasi koneksi ke Zona Dapur (AI Microservice / FastAPI).
    | URL internal Docker: http://dapur-ai:8000
    |
    */

    'dapur_ai' => [
        'base_url' => env('DAPUR_AI_URL', 'http://dapur-ai:8000'),
        'timeout'  => (int) env('DAPUR_AI_TIMEOUT', 300),
        'endpoint' => '/api/generate-rks',
    ],

];
