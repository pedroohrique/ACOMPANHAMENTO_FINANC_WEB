export default async function handler(req, res) {
  try {
    // Pega o caminho real vindo do rewrite do vercel.json
    let path = req.query?.realPath || '';
    if (Array.isArray(path)) {
      path = path.join('/');
    }
    path = String(path || '');

    // Limpa os parâmetros de busca para não passar o 'realPath' adiante
    const host = req.headers?.host || 'localhost';
    const urlObj = new URL(req.url || '/', `http://${host}`);
    const searchParams = new URLSearchParams(urlObj.search);
    searchParams.delete('realPath');
    const cleanSearch = searchParams.toString() ? `?${searchParams.toString()}` : '';
    
    const targetUrl = `https://noncongruous-chiffonade-bernarda.ngrok-free.dev/api/${path}${cleanSearch}`;

    const fetchOptions = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': req.headers['authorization'] || '',
        'X-Auth-Token': req.headers['x-auth-token'] || '',
        'X-API-Key': req.headers['x-api-key'] || 'pedro_financas_2026_seguro_!@',
        'ngrok-skip-browser-warning': 'true',
        'User-Agent': 'Vercel-Proxy'
      }
    };

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      fetchOptions.body = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    }

    const response = await fetch(targetUrl, fetchOptions);

    // Tenta ler como JSON, se falhar pega como texto (evita 502 por crash)
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = { detail: text };
    }
    
    // Adiciona headers de CORS para garantir
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Auth-Token, X-API-Key');
    
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Proxy Error:', error);
    res.status(500).json({ 
      detail: `Falha na conexão com o servidor (ngrok): ${error.message}`,
      // Inclui contexto para debugar erros 502/edge cases
      name: error?.name,
      stack: error?.stack,
      method: req?.method,
      url: req?.url
    });
  }
}
