import handler from './api/index.js';

const req = {
  url: '/api/index?realPath=transacoes/123/recorrencia',
  method: 'POST',
  headers: {
    host: 'localhost:3000',
    authorization: 'Bearer token123'
  },
  query: {
    realPath: 'transacoes/123/recorrencia'
  },
  body: { recorrente: true }
};

const res = {
  setHeader: (key, val) => console.log(`SetHeader: ${key} = ${val}`),
  status: (code) => {
    console.log(`Status: ${code}`);
    return {
      json: (data) => console.log(`JSON:`, data)
    };
  }
};

handler(req, res).catch(console.error);
