export default async function handler(req, res) {
  // Pega o caminho após /api/
  const urlObj = new URL(req.url, `http://${req.headers.host}`);
  const path = urlObj.pathname.replace('/api/', '');
  const search = urlObj.search;
  
  const targetUrl = `https://noncongruous-chiffonade-bernarda.ngrok-free.dev/api/${path}${search}`;

  try {
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': req.headers['authorization'] || '',
        'X-Auth-Token': req.headers['x-auth-token'] || '',
        'X-API-Key': 'pedro_financas_2026_seguro_!@',
        'ngrok-skip-browser-warning': 'true',
        'User-Agent': 'Vercel-Proxy'
      },
      body: req.method !== 'GET' && req.method !== 'HEAD' ? JSON.stringify(req.body) : undefined
    });

    const data = await response.json();
    
    // Adiciona headers de CORS para garantir
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Auth-Token');
    
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Proxy Error:', error);
    res.status(500).json({ detail: `Falha na conexão com o servidor local: ${error.message}` });
  }
}
