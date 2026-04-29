import { useState, useEffect, useMemo } from 'react'
import { 
  LayoutDashboard, 
  Receipt, 
  CreditCard, 
  TrendingUp, 
  TrendingDown, 
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  Filter,
  LogOut,
  Calendar,
  FileText,
  Trash2,
  Edit,
  Search,
  MoreVertical,
  X,
  Zap,
  DollarSign,
  Download,
  User,
  Mail,
  Lock,
  UserPlus
} from 'lucide-react'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  LabelList
} from 'recharts'
import './App.css'

// API Base URL from environment or default to local
const API_URL = import.meta.env.VITE_API_URL || 'https://noncongruous-chiffonade-bernarda.ngrok-free.dev';

function App() {
  // Auth States
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')))
  const [authStep, setAuthStep] = useState('login') // login, register, verify
  const [authForm, setAuthForm] = useState({ nome: '', email: '', password: '', code: '' })
  const [authMessage, setAuthMessage] = useState({ text: '', type: '' })

  // Dashboard States
  const [activeTab, setActiveTab] = useState('dashboard')
  const [fluxo, setFluxo] = useState(null)
  const [resumoMensal, setResumoMensal] = useState([])
  const [gastosCategoria, setGastosCategoria] = useState([])
  const [transacoes, setTransacoes] = useState([])
  const [debitosPendentes, setDebitosPendentes] = useState([])
  const [reportOverview, setReportOverview] = useState(null)
  const [categoriasMap, setCategoriasMap] = useState({})
  const [formasMap, setFormasMap] = useState({})
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  const [showModal, setShowModal] = useState(false)
  const [modalMode, setModalMode] = useState('cadastrar') 
  const [showExportModal, setShowExportModal] = useState(false)

  const [formData, setFormData] = useState({
    id: null, dt_gasto: '', valor: '', descricao: '', categoria: '', local: '', forma_pagamento: '', parcelamento: 'Não', n_parcelas: '1'
  })

  const [exportData, setExportData] = useState({
    mes: new Date().getMonth() + 1,
    ano: new Date().getFullYear()
  })

  const currentYear = new Date().getFullYear()
  const currentMonth = new Date().getMonth() + 1

  const monthsList = [
    { id: 1, name: 'Janeiro' }, { id: 2, name: 'Fevereiro' }, { id: 3, name: 'Março' },
    { id: 4, name: 'Abril' }, { id: 5, name: 'Maio' }, { id: 6, name: 'Junho' },
    { id: 7, name: 'Julho' }, { id: 8, name: 'Agosto' }, { id: 9, name: 'Setembro' },
    { id: 10, name: 'Outubro' }, { id: 11, name: 'Novembro' }, { id: 12, name: 'Dezembro' }
  ]

  // Helper for headers
  const getHeaders = () => ({
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': '69420',
    'Authorization': `Bearer ${token}`
  });

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
    setAuthStep('login')
  }

  const handleAuthSubmit = async (e) => {
    e.preventDefault()
    setAuthMessage({ text: '', type: '' })
    setLoading(true)

    try {
      if (authStep === 'register') {
        const res = await fetch(`${API_URL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': '69420' },
          body: JSON.stringify({ nome: authForm.nome, email: authForm.email, password: authForm.password })
        })
        const data = await res.json()
        if (res.ok) {
          setAuthMessage({ text: 'Cadastro realizado! Verifique o código no console do servidor.', type: 'success' })
          setAuthStep('verify')
        } else {
          setAuthMessage({ text: data.detail || 'Erro ao registrar', type: 'error' })
        }
      } 
      else if (authStep === 'verify') {
        const res = await fetch(`${API_URL}/api/auth/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': '69420' },
          body: JSON.stringify({ email: authForm.email, code: authForm.code })
        })
        const data = await res.json()
        if (res.ok) {
          setAuthMessage({ text: 'E-mail verificado! Agora você pode fazer login.', type: 'success' })
          setAuthStep('login')
        } else {
          setAuthMessage({ text: data.detail || 'Código inválido', type: 'error' })
        }
      }
      else if (authStep === 'login') {
        const res = await fetch(`${API_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': '69420' },
          body: JSON.stringify({ email: authForm.email, password: authForm.password })
        })
        const data = await res.json()
        if (res.ok) {
          localStorage.setItem('token', data.access_token)
          localStorage.setItem('user', JSON.stringify(data.user))
          setToken(data.access_token)
          setUser(data.user)
        } else {
          setAuthMessage({ text: data.detail || 'Credenciais inválidas', type: 'error' })
        }
      }
    } catch (error) {
      setAuthMessage({ text: 'Erro de conexão com o servidor', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  const fetchData = async () => {
    if (!token) return
    try {
      setLoading(true)
      const fetchOptions = { headers: getHeaders() };
      const [resFluxo, resResumo, resCategorias, resTrans, resDebitos, resReport, resCats, resWays] = await Promise.all([
        fetch(`${API_URL}/api/fluxo-caixa/${currentYear}/${currentMonth}`, fetchOptions),
        fetch(`${API_URL}/api/resumo-mensal/${currentYear}`, fetchOptions),
        fetch(`${API_URL}/api/gastos-por-categoria/${currentYear}/${currentMonth}`, fetchOptions),
        fetch(`${API_URL}/api/transacoes`, fetchOptions),
        fetch(`${API_URL}/api/debitos-pendentes`, fetchOptions),
        fetch(`${API_URL}/api/visao-geral-relatorio/${currentYear}/${currentMonth}`, fetchOptions),
        fetch(`${API_URL}/api/categorias`, fetchOptions),
        fetch(`${API_URL}/api/formas-pagamento`, fetchOptions)
      ])

      // Se qualquer um retornar 401, desloga
      if (resFluxo.status === 401) return handleLogout()

      const dFluxo = await resFluxo.json()
      const dResumo = await resResumo.json()
      const dCategorias = await resCategorias.json()
      const dTrans = await resTrans.json()
      const dDebitos = await resDebitos.json()
      const dReport = await resReport.json()
      const dCats = await resCats.json()
      const dWays = await resWays.json()

      setFluxo(dFluxo.fluxo)
      const cleanResumo = (dResumo.resumo || []).map(item => ({
        ...item,
        gasto: typeof item.gasto === 'string' 
          ? parseFloat(item.gasto.replace(/[R$\s.]/g, '').replace(',', '.')) || 0 
          : parseFloat(item.gasto) || 0
      }))
      setResumoMensal(cleanResumo)
      setTransacoes(dTrans.transacoes || [])
      setDebitosPendentes(dDebitos.debitos || [])
      setReportOverview(dReport)
      setCategoriasMap(dCats.categorias || {})
      setFormasMap(dWays.formas_pagamento || {})

      const formattedCats = Object.entries(dCategorias.gastos || {}).map(([name, value]) => ({
        name,
        value: parseFloat(value) || 0
      })).filter(cat => cat.value > 0)
      setGastosCategoria(formattedCats)

    } catch (error) {
      console.error("Erro ao buscar dados:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (token) fetchData()
  }, [token])

  const filteredTransacoes = useMemo(() => {
    if (!searchTerm) return transacoes
    const lowerSearch = searchTerm.toLowerCase()
    return transacoes.filter(t => 
      t.descricao?.toLowerCase().includes(lowerSearch) ||
      t.local?.toLowerCase().includes(lowerSearch) ||
      t.categoria?.toLowerCase().includes(lowerSearch)
    )
  }, [transacoes, searchTerm])

  const handleDelete = async (id) => {
    if (window.confirm("Deseja realmente excluir este lançamento?")) {
      try {
        const response = await fetch(`${API_URL}/api/transacoes/${id}`, { 
          method: 'DELETE',
          headers: getHeaders()
        })
        if (response.ok) fetchData()
      } catch (error) {
        console.error("Erro delete:", error)
      }
    }
  }

  const openModal = (mode, data = null) => {
    setModalMode(mode)
    if (data) {
      let formattedDate = ''
      if (data.dt_compra) {
        const parts = data.dt_compra.split('/')
        if (parts.length === 3) formattedDate = `${parts[2]}-${parts[1]}-${parts[0]}`
      }
      
      let valorLimpo = data.valor_parcela;
      if (typeof valorLimpo === 'string') {
        valorLimpo = valorLimpo.replace(/[R$\s]/g, '').replace(/\./g, '').replace(',', '.');
      }

      setFormData({
        id: data.id,
        dt_gasto: formattedDate,
        valor: valorLimpo || '',
        descricao: data.descricao || '',
        categoria: data.categoria?.toUpperCase() || '',
        local: data.local || '',
        forma_pagamento: data.forma_pagamento?.toUpperCase() || '',
        parcelamento: data.parcelamento === 'S' ? 'Sim' : 'Não',
        n_parcelas: data.n_parcelas || '1'
      })
    } else {
      setFormData({
        id: null, dt_gasto: new Date().toISOString().split('T')[0], valor: '', descricao: '', categoria: '', local: '', forma_pagamento: '', parcelamento: 'Não', n_parcelas: '1'
      })
    }
    setShowModal(true)
  }

  const handleModalSubmit = async (e) => {
    e.preventDefault()
    try {
      const url = modalMode === 'cadastrar' ? `${API_URL}/api/transacoes` : `${API_URL}/api/transacoes/${formData.id}`
      const method = modalMode === 'cadastrar' ? 'POST' : 'PUT'
      
      const body = {
        dt_gasto: formData.dt_gasto,
        valor: parseFloat(formData.valor),
        desc: formData.descricao,
        desc_local: formData.local,
        flag_parcelamento: formData.parcelamento === 'Sim' ? 'S' : 'N',
        qt_parcelas: parseInt(formData.n_parcelas) || 1,
        desc_categoria: categoriasMap[formData.categoria],
        forma_pagamento: formasMap[formData.forma_pagamento]
      }

      const response = await fetch(url, {
        method,
        headers: getHeaders(),
        body: JSON.stringify(body)
      })

      if (response.ok) {
        setShowModal(false)
        fetchData()
      } else {
        const err = await response.json()
        alert(`Erro na operação: ${err.detail || 'Verifique os dados'}`)
      }
    } catch (error) {
      console.error("Erro submit:", error)
    }
  }

  const handleExportSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch(`${API_URL}/api/exportar-relatorio`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ mes: parseInt(exportData.mes), ano: parseInt(exportData.ano) })
      })

      if (response.ok) {
        const res = await response.json()
        alert(`Relatório exportado com sucesso!\nSalvo em: ${res.path}`)
        setShowExportModal(false)
      } else {
        const err = await response.json()
        alert(`Erro ao exportar: ${err.detail || 'Verifique os dados'}`)
      }
    } catch (error) {
      console.error("Erro export:", error)
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value || 0)
  }

  // --- VIEW: LOGIN / REGISTER ---
  if (!token) {
    return (
      <div className="auth-container">
        <div className="auth-card glass animate-fade-in">
          <div className="auth-header">
            <div className="logo-icon large"><Wallet size={40} color="#10b981" /></div>
            <h2>{authStep === 'login' ? 'Bem-vindo de volta' : authStep === 'register' ? 'Criar nova conta' : 'Verificação'}</h2>
            <p className="auth-subtitle">
              {authStep === 'login' ? 'Acesse seu controle financeiro' : authStep === 'register' ? 'Cadastre-se para começar' : 'Insira o código enviado (veja o terminal)'}
            </p>
          </div>

          <form className="auth-form" onSubmit={handleAuthSubmit}>
            {authStep === 'register' && (
              <div className="form-group">
                <label><User size={16} /> Nome Completo</label>
                <input type="text" placeholder="Seu nome" value={authForm.nome} onChange={e => setAuthForm({...authForm, nome: e.target.value})} required />
              </div>
            )}
            <div className="form-group">
              <label><Mail size={16} /> E-mail</label>
              <input type="email" placeholder="email@exemplo.com" value={authForm.email} onChange={e => setAuthForm({...authForm, email: e.target.value})} required />
            </div>
            {authStep !== 'verify' && (
              <div className="form-group">
                <label><Lock size={16} /> Senha</label>
                <input type="password" placeholder="••••••••" value={authForm.password} onChange={e => setAuthForm({...authForm, password: e.target.value})} required />
              </div>
            )}
            {authStep === 'verify' && (
              <div className="form-group">
                <label><Zap size={16} /> Código de Verificação</label>
                <input type="text" placeholder="123456" value={authForm.code} onChange={e => setAuthForm({...authForm, code: e.target.value})} required />
              </div>
            )}

            {authMessage.text && <div className={`auth-alert ${authMessage.type}`}>{authMessage.text}</div>}

            <button type="submit" className="btn btn-primary full-width" disabled={loading}>
              {loading ? 'Aguarde...' : authStep === 'login' ? 'Entrar' : authStep === 'register' ? 'Registrar' : 'Verificar'}
            </button>
          </form>

          <div className="auth-footer">
            {authStep === 'login' ? (
              <p>Não tem uma conta? <button onClick={() => setAuthStep('register')}>Cadastre-se</button></p>
            ) : (
              <p>Já tem uma conta? <button onClick={() => setAuthStep('login')}>Faça login</button></p>
            )}
          </div>
        </div>
      </div>
    )
  }

  const daysRemaining = (() => {
    const today = new Date()
    const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate()
    return lastDay - today.getDate() + 1
  })()
  const recommendedDaily = reportOverview ? (reportOverview.valor_disponivel / daysRemaining) : 0
  const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316']

  return (
    <div className="app-container">
      <aside className="sidebar glass">
        <div className="sidebar-logo"><div className="logo-icon"><Wallet size={24} color="#10b981" /></div><h1>Finance</h1></div>
        <div className="user-profile">
            <div className="user-avatar">{user?.nome?.charAt(0) || 'U'}</div>
            <div className="user-info">
                <p className="user-name">{user?.nome || 'Usuário'}</p>
                <p className="user-email">{user?.email}</p>
            </div>
        </div>
        <nav className="sidebar-nav">
          <button className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}><LayoutDashboard size={20} /><span>Dashboard</span></button>
          <button className={`nav-item ${activeTab === 'transactions' ? 'active' : ''}`} onClick={() => setActiveTab('transactions')}><Receipt size={20} /><span>Lançamentos</span></button>
        </nav>
        <div className="sidebar-footer"><button className="nav-item logout" onClick={handleLogout}><LogOut size={20} /><span>Sair</span></button></div>
      </aside>

      <main className="main-content">
        <header className="main-header">
          <div className="header-search"><h2>{activeTab === 'dashboard' ? 'Dashboard' : 'Lançamentos'}</h2></div>
          <div className="header-actions">
            {activeTab === 'dashboard' && <button className="btn btn-secondary glass" onClick={() => setShowExportModal(true)}><Download size={18} /><span>Exportar</span></button>}
            <button className="btn btn-primary" onClick={() => openModal('cadastrar')}><Plus size={18} /><span>Novo Registro</span></button>
          </div>
        </header>

        {loading && <div className="loading-state"><p>Carregando...</p></div>}
        
        {activeTab === 'dashboard' ? (
          <div className="dashboard-view animate-fade-in">
            <div className="stats-row">
              <StatCard title="Entradas" value={formatCurrency(fluxo?.vl_entradas)} icon={TrendingUp} type="income" />
              <StatCard title="Gasto do Mês" value={formatCurrency(reportOverview?.total_gastos)} icon={Receipt} type="expense" />
              <StatCard title="Saldo Atual" value={formatCurrency(fluxo?.saldo_atual)} icon={Wallet} type="balance" />
              <StatCard title="Valor Disponível" value={formatCurrency(reportOverview?.valor_disponivel)} icon={DollarSign} type="average" subtitle="Livre para uso" />
              <StatCard title="Recomendado" value={formatCurrency(recommendedDaily)} icon={Zap} type="warning" subtitle="Limite diário" />
            </div>
            <div className="charts-row">
              <div className="chart-container glass">
                <h3>Fluxo Mensal</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={resumoMensal}>
                    <defs>
                      <linearGradient id="colorGasto" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="mes" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `R$ ${val}`} />
                    <Tooltip 
                      formatter={(value) => formatCurrency(value)} 
                      contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.3)' }} 
                    />
                    <Bar name="Gasto" dataKey="gasto" fill="#3b82f6" radius={[6, 6, 0, 0]}>
                      {resumoMensal.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill="url(#colorGasto)" />
                      ))}
                      <LabelList 
                        dataKey="gasto" 
                        position="top" 
                        formatter={(val) => val > 0 ? formatCurrency(val).replace('R$', '').trim() : ''}
                        style={{ fill: '#94a3b8', fontSize: '11px', fontWeight: '600' }}
                      />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="chart-container glass">
                <h3>Gastos por Categoria</h3>
                <div className="category-layout">
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie data={gastosCategoria} cx="50%" cy="50%" innerRadius={50} outerRadius={70} paddingAngle={5} dataKey="value">
                        {gastosCategoria.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                      </Pie>
                      <Tooltip formatter={(value) => `R$ ${value.toFixed(2)}`} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="category-table-mini">
                    <table>
                      <tbody>
                        {gastosCategoria.map((cat, idx) => (
                          <tr key={idx}>
                            <td><span className="dot" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span></td>
                            <td className="cat-name">{cat.name}</td>
                            <td className="cat-val">R$ {cat.value.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
            <div className="report-section glass" style={{ marginBottom: '24px' }}>
              <h3>Débitos Pendentes</h3>
              <div className="table-container">
                <table className="modern-table">
                  <thead><tr><th>Descrição</th><th>Parcelas</th><th>Vlr Total</th><th>Vlr Pendente</th><th>Último Pgto</th></tr></thead>
                  <tbody>
                    {debitosPendentes.length > 0 ? debitosPendentes.map((deb, idx) => (
                      <tr key={idx}><td>{deb.descricao}</td><td>{deb.parcelas_pendentes}</td><td>{deb.valor_total}</td><td className="text-danger">{deb.valor_pendente}</td><td>{deb.mes_ultimo_debito}/{deb.ano_ultimo_debito}</td></tr>
                    )) : <tr><td colSpan="5" style={{ textAlign: 'center', padding: '20px' }}>Nenhum débito pendente.</td></tr>}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="report-section glass">
              <h3>Resumo Anual Consolidado - {currentYear}</h3>
              <div className="table-container">
                <table className="modern-table consolidated">
                  <thead><tr><th>Mês</th><th>Ano</th><th>Orçamento</th><th>Gasto</th><th>Saldo</th><th>% Uso</th><th>Qtd</th><th>Maior</th><th>Acumulado</th><th>Var</th><th>% Var</th></tr></thead>
                  <tbody>
                    {resumoMensal.map((item, idx) => (
                      <tr key={idx}>
                        <td>{item.mes}</td>
                        <td>{item.ano}</td>
                        <td>{formatCurrency(item.orcamento)}</td>
                        <td>{formatCurrency(item.gasto)}</td>
                        <td className={String(item.saldo).includes('-') ? "text-danger" : "text-success"}>{formatCurrency(item.saldo)}</td>
                        <td>{item.percentual != null ? `${Number(item.percentual).toFixed(2)}%` : '-'}</td>
                        <td>{item.qtd}</td>
                        <td>{formatCurrency(item.maior_gasto)}</td>
                        <td>{formatCurrency(item.acumulado)}</td>
                        <td>{item.variacao != null ? formatCurrency(item.variacao) : '-'}</td>
                        <td>{item.percentual_var != null ? `${Number(item.percentual_var).toFixed(2)}%` : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="transactions-view animate-fade-in">
            <div className="view-header">
              <div className="search-bar-container glass">
                <Search size={18} color="#94a3b8" /><input type="text" placeholder="Pesquisar..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
              </div>
              <button className="btn btn-secondary glass"><Filter size={18} /><span>Filtros</span></button>
            </div>
            <div className="table-card glass">
              <div className="table-container">
                <table className="modern-table">
                  <thead><tr><th>Data</th><th>Pagto</th><th>Descrição</th><th>Categoria</th><th>Local</th><th>Total</th><th>Parcela</th><th>Pendente</th><th>Forma</th><th>Ações</th></tr></thead>
                  <tbody>
                    {filteredTransacoes.map((t) => (
                      <tr key={t.id}><td>{t.dt_compra}</td><td>{t.dt_pagamento}</td><td className="font-semibold">{t.descricao}</td><td><span className="badge-category">{t.categoria}</span></td><td>{t.local}</td><td>{t.total}</td><td>{t.valor_parcela}</td><td className={t.valor_pendente !== "R$ 0,00" ? "text-danger" : ""}>{t.valor_pendente}</td><td>{t.forma_pagamento}</td><td><div className="action-buttons"><button className="action-btn edit" onClick={() => openModal('atualizar', t)}><Edit size={16} /></button><button className="action-btn delete" onClick={() => handleDelete(t.id)}><Trash2 size={16} /></button></div></td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content glass animate-fade-in">
            <div className="modal-header"><h3>{modalMode === 'cadastrar' ? 'Novo Registro' : 'Atualizar'}</h3><button onClick={() => setShowModal(false)}><X size={20} /></button></div>
            <form className="modal-form" onSubmit={handleModalSubmit}>
              <div className="form-row"><div className="form-group"><label>Data</label><input type="date" value={formData.dt_gasto} onChange={e => setFormData({...formData, dt_gasto: e.target.value})} required /></div><div className="form-group"><label>Valor (R$)</label><input type="number" step="0.01" value={formData.valor} onChange={e => setFormData({...formData, valor: e.target.value})} required /></div></div>
              <div className="form-group"><label>Descrição</label><input type="text" value={formData.descricao} onChange={e => setFormData({...formData, descricao: e.target.value})} required /></div>
              <div className="form-row"><div className="form-group"><label>Categoria</label><select value={formData.categoria} onChange={e => setFormData({...formData, categoria: e.target.value})} required><option value="">Selecione...</option>{Object.keys(categoriasMap).map(cat => <option key={cat} value={cat}>{cat}</option>)}</select></div><div className="form-group"><label>Local</label><input type="text" value={formData.local} onChange={e => setFormData({...formData, local: e.target.value})} required /></div></div>
              <div className="form-row"><div className="form-group"><label>Forma</label><select value={formData.forma_pagamento} onChange={e => setFormData({...formData, forma_pagamento: e.target.value})} required><option value="">Selecione...</option>{Object.keys(formasMap).map(forma => <option key={forma} value={forma}>{forma}</option>)}</select></div><div className="form-group"><label>Parcelamento</label><select value={formData.parcelamento} onChange={e => setFormData({...formData, parcelamento: e.target.value})}><option value="Sim">Sim</option><option value="Não">Não</option></select></div></div>
              {formData.parcelamento === 'Sim' && <div className="form-group"><label>Parcelas</label><input type="number" value={formData.n_parcelas} onChange={e => setFormData({...formData, n_parcelas: e.target.value})} required /></div>}
              <div className="modal-footer"><button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancelar</button><button type="submit" className="btn btn-primary">Salvar</button></div>
            </form>
          </div>
        </div>
      )}

      {showExportModal && (
        <div className="modal-overlay">
          <div className="modal-content glass animate-fade-in" style={{ maxWidth: '400px' }}>
            <div className="modal-header"><h3>Exportar PDF</h3><button onClick={() => setShowExportModal(false)}><X size={20} /></button></div>
            <form className="modal-form" onSubmit={handleExportSubmit}>
              <div className="form-group"><label>Mês</label><select value={exportData.mes} onChange={e => setExportData({...exportData, mes: e.target.value})} required>{monthsList.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}</select></div>
              <div className="form-group"><label>Ano</label><input type="number" value={exportData.ano} onChange={e => setExportData({...exportData, ano: e.target.value})} required /></div>
              <div className="modal-footer"><button type="button" className="btn btn-secondary" onClick={() => setShowExportModal(false)}>Cancelar</button><button type="submit" className="btn btn-primary">Gerar</button></div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

function StatCard({ title, value, icon: Icon, type, subtitle }) {
  return (
    <div className="stat-card glass">
      <div className="stat-header"><div className={`stat-icon ${type}`}><Icon size={20} /></div><span className="stat-title">{title}</span></div>
      <div className="stat-body"><h2 className="stat-value">{value}</h2>{subtitle && <p className="stat-subtitle">{subtitle}</p>}</div>
    </div>
  )
}

export default App
