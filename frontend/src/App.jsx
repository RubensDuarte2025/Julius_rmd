import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useLocation } from 'react-router-dom';

import MesasDashboardPage from './pages/atendimento/MesasDashboardPage';
import PedidoMesaOperacaoPage from './pages/atendimento/PedidoMesaOperacaoPage';
import CozinhaDashboardPageActual from './pages/cozinha/CozinhaDashboardPage'; // Importa a página real

// Admin Pages and Layout
import AdminLayout from './components/admin/layout/AdminLayout';
import AdminDashboardPageActual from './pages/admin/AdminDashboardPage';
import GerenciarCategoriasPage from './pages/admin/GerenciarCategoriasPage';
import GerenciarProdutosPage from './pages/admin/GerenciarProdutosPage';
import GerenciarMesasPage from './pages/admin/GerenciarMesasPage';
import GerenciarConfiguracoesPage from './pages/admin/GerenciarConfiguracoesPage';
import RelatorioVendasPage from './pages/admin/RelatorioVendasPage';
import RelatorioProdutosPage from './pages/admin/RelatorioProdutosPage';


// Placeholder components for pages - to be developed later
const HomePage = () => <h2>Página Inicial (Frontend)</h2>;
const LoginPage = () => <h2>Página de Login (Pós-MVP)</h2>;
// const AdminDashboardPage = () => <h2>Admin - Dashboard</h2>; // Substituído por AdminDashboardPageActual

// Simple Navbar (Consider moving this to a Layout component if not using AdminLayout for all)
// TODO: Refatorar Navbar para usar componentes MUI como AppBar, Toolbar, Button, Typography
// Exemplo:
// import AppBar from '@mui/material/AppBar';
// import Toolbar from '@mui/material/Toolbar';
// import Typography from '@mui/material/Typography';
// import Button from '@mui/material/Button'; (ou StyledButton)
//
// const MainNavbar = () => (
//   <AppBar position="static">
//     <Toolbar>
//       <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
//         PizzeriaSaaS
//       </Typography>
//       <Button color="inherit" component={Link} to="/">Home App</Button>
//       <Button color="inherit" component={Link} to="/atendimento/mesas">Atendimento</Button>
//       <Button color="inherit" component={Link} to="/cozinha">Cozinha</Button>
//       <Button color="inherit" component={Link} to="/admin/dashboard">Admin</Button>
//       <Button color="inherit" component={Link} to="/login">Login (Pós-MVP)</Button>
//     </Toolbar>
//   </AppBar>
// );
// E então usar <MainNavbar /> no lugar da const Navbar abaixo.

const Navbar = () => ( // Este é o Navbar placeholder atual
  <nav style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    gap: '20px', 
    padding: '10px', 
    backgroundColor: '#333', 
    color: 'white' 
  }}>
    <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Home App</Link>
    <Link to="/atendimento/mesas" style={{ color: 'white', textDecoration: 'none' }}>Atendimento</Link>
    <Link to="/cozinha" style={{ color: 'white', textDecoration: 'none' }}>Cozinha</Link>
    <Link to="/admin/dashboard" style={{ color: 'white', textDecoration: 'none' }}>Admin</Link>
    <Link to="/login" style={{ color: 'white', textDecoration: 'none' }}>Login (Pós-MVP)</Link>
  </nav>
);


// Determine if AdminLayout should be used based on the current path
const AppContent = () => {
  const location = useLocation(); // from react-router-dom
  
  // This simple Navbar is shown for non-admin routes for MVP.
  // For a real app, you'd have a more sophisticated layout strategy.
  const showMainNavbar = !location.pathname.startsWith('/admin');

  return (
    <>
      {showMainNavbar && <Navbar />}
      <div style={showMainNavbar ? { padding: '20px' } : {}}> {/* No padding if AdminLayout handles it */}
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          
          {/* Rotas do Módulo de Atendimento */}
          <Route path="/atendimento/mesas" element={<MesasDashboardPage />} />
          <Route path="/atendimento/mesas/:mesaId/pedido" element={<PedidoMesaOperacaoPage />} />

          {/* Rota do Módulo da Cozinha */}
          <Route path="/cozinha" element={<CozinhaDashboardPageActual />} />
          
          {/* Rotas do Módulo de Administração com AdminLayout */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route path="dashboard" element={<AdminDashboardPageActual />} />
            <Route path="cardapio/categorias" element={<GerenciarCategoriasPage />} />
            <Route path="cardapio/produtos" element={<GerenciarProdutosPage />} />
            <Route path="mesas" element={<GerenciarMesasPage />} />
            <Route path="configuracoes" element={<GerenciarConfiguracoesPage />} />
            <Route path="relatorios/vendas" element={<RelatorioVendasPage />} />
            <Route path="relatorios/produtos" element={<RelatorioProdutosPage />} />
            {/* Adicionar um redirect para /admin/dashboard se /admin for acessado */}
            <Route index element={<AdminDashboardPageActual />} /> 
          </Route>
          
          <Route path="*" element={<div>Página não encontrada (404)</div>} />
        </Routes>
      </div>
    </>
  );
}


function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;

// Adicionar useLocation no import do react-router-dom
// import { BrowserRouter as Router, Route, Routes, Link, useLocation } from 'react-router-dom';
// Vou fazer essa correção no próximo passo se o replace não pegar isso.
