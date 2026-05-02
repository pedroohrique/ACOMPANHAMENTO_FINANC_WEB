export default async function handler(req, res) {
  // Pega o caminho real vindo do rewrite do vercel.json
  let path = req.query.realPath || '';
  if (Array.isArray(path)) {
    path = path.join('/');
  }

  // Limpa os parâmetros de busca para não passar o 'realPath' adiante
  const urlObj = new URL(req.url, `http://${req.headers.host}`);
  const searchParams = new URLSearchParams(urlObj.search);
  searchParams.delete('realPath');
  const cleanSearch = searchParams.toString() ? `?${searchParams.toString()}` : '';
  
  const targetUrl = `https://noncongruous-chiffonade-bernarda.ngrok-free.dev/api/${path}${cleanSearch}`;

  try {
    const fetchOptions = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': req.headers['authorization'] || '',
        'X-Auth-Token': req.headers['x-auth-token'] || '',
        'User-Agent': 'Vercel-Proxy'
      }
    };

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      fetchOptions.body = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    }

    const response = await fetch(targetUrl, fetchOptions);

    // Tenta ler como JSON, se falhar pega como texto
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = { detail: text };
    }
    
    // Headers de CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Auth-Token, X-API-Key');
    
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Proxy Error:', error);
    res.status(500).json({ 
      detail: `Falha na conexão com o servidor local: ${error.message}`,
      target: targetUrl 
    });
  }
}
