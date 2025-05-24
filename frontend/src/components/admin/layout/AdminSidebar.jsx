import React from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom'; // Renomear Link para RouterLink
// import Drawer from '@mui/material/Drawer';
// import List from '@mui/material/List';
// import ListItem from '@mui/material/ListItem';
// import ListItemButton from '@mui/material/ListItemButton';
// import ListItemIcon from '@mui/material/ListItemIcon';
// import ListItemText from '@mui/material/ListItemText';
// import Typography from '@mui/material/Typography';
// import Divider from '@mui/material/Divider';
// Exemplo de ícones:
// import DashboardIcon from '@mui/icons-material/Dashboard';
// import CategoryIcon from '@mui/icons-material/Category';
// import FastfoodIcon from '@mui/icons-material/Fastfood';
// import TableRestaurantIcon from '@mui/icons-material/TableRestaurant';
// import SettingsIcon from '@mui/icons-material/Settings';
// import AssessmentIcon from '@mui/icons-material/Assessment';

// TODO: Refatorar AdminSidebar para usar componentes MUI (Drawer, List, ListItem, etc.)
// A estrutura abaixo é um exemplo de como poderia ser:
/*
const drawerWidth = 250;

const MUIAdminSidebar = () => {
  const location = useLocation();
  const menuItems = [
    { text: 'Dashboard', path: '/admin/dashboard', icon: <DashboardIcon /> },
    { text: 'Categorias', path: '/admin/cardapio/categorias', icon: <CategoryIcon /> },
    { text: 'Produtos', path: '/admin/cardapio/produtos', icon: <FastfoodIcon /> },
    { text: 'Mesas', path: '/admin/mesas', icon: <TableRestaurantIcon /> },
    { text: 'Configurações', path: '/admin/configuracoes', icon: <SettingsIcon /> },
  ];
  const reportItems = [
    { text: 'Vendas', path: '/admin/relatorios/vendas', icon: <AssessmentIcon /> },
    { text: 'Produtos Vendidos', path: '/admin/relatorios/produtos', icon: <AssessmentIcon /> },
  ];

  const listContent = (
    <div>
      <Toolbar> // Para alinhar com AppBar se houver
        <Typography variant="h6" noWrap component="div">
          Admin Pizzeria
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding component={RouterLink} to={item.path} sx={{ color: 'inherit', textDecoration: 'none' }}>
            <ListItemButton selected={location.pathname.startsWith(item.path)}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <Typography variant="overline" sx={{ pl: 2 }}>Relatórios</Typography>
        {reportItems.map((item) => (
          <ListItem key={item.text} disablePadding component={RouterLink} to={item.path} sx={{ color: 'inherit', textDecoration: 'none' }}>
            <ListItemButton selected={location.pathname.startsWith(item.path)}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Drawer
      variant="permanent" // Ou 'temporary' para mobile
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      {listContent}
    </Drawer>
  );
};
*/


// Mantendo a implementação atual com estilos inline por enquanto
const AdminSidebar = () => {
  const location = useLocation();

  const sidebarStyle = {
    width: '250px',
    backgroundColor: '#f8f9fa', // Um cinza claro
    padding: '20px',
    height: '100vh', // Altura total da viewport
    borderRight: '1px solid #dee2e6', // Borda sutil
    boxSizing: 'border-box',
  };

  const navStyle = {
    display: 'flex',
    flexDirection: 'column',
  };

  const linkStyle = (path) => ({ // RouterLink do react-router-dom
    padding: '10px 15px',
    margin: '5px 0',
    textDecoration: 'none',
    color: location.pathname.startsWith(path) ? '#007bff' : '#343a40', // Cor ativa e cor padrão
    backgroundColor: location.pathname.startsWith(path) ? '#e9ecef' : 'transparent', // Fundo para link ativo
    borderRadius: '5px', // Usar theme.shape.borderRadius do MUI
    transition: 'background-color 0.2s ease, color 0.2s ease', // Usar theme.transitions do MUI
  });

  // As funções hoverStyle e leaveStyle podem ser substituídas por pseudo-classes CSS (:hover)
  // ou pela prop `sx` do MUI com pseudo-classes.
  // Exemplo com sx:
  // sx={{
  //   padding: '10px 15px', margin: '5px 0', textDecoration: 'none', borderRadius: '5px',
  //   color: location.pathname.startsWith(path) ? 'primary.main' : 'text.primary',
  //   backgroundColor: location.pathname.startsWith(path) ? 'action.selected' : 'transparent',
  //   '&:hover': {
  //     backgroundColor: 'action.hover',
  //     color: 'primary.dark',
  //   },
  // }}
  
  const headingStyle = {
    fontSize: '1.2em',
    color: '#495057',
    paddingBottom: '10px',
    borderBottom: '1px solid #ced4da',
    marginBottom: '15px',
  };


  return (
    <div style={sidebarStyle}>
      <h3 style={headingStyle}>Admin Pizzeria</h3>
      <nav style={navStyle}>
        <RouterLink 
          to="/admin/dashboard" 
          style={linkStyle("/admin/dashboard")}
          // onMouseEnter e onMouseLeave seriam substituídos por estilização MUI :hover
        >
          Dashboard
        </RouterLink>
        
        <h4 style={{...headingStyle, fontSize: '1em', marginTop: '15px', marginBottom: '5px'}}>Gerenciar</h4>
        <RouterLink 
          to="/admin/cardapio/categorias" 
          style={linkStyle("/admin/cardapio/categorias")}
        >
          Categorias
        </RouterLink>
        <RouterLink 
          to="/admin/cardapio/produtos" 
          style={linkStyle("/admin/cardapio/produtos")}
        >
          Produtos
        </RouterLink>
        <RouterLink 
          to="/admin/mesas" 
          style={linkStyle("/admin/mesas")}
        >
          Mesas
        </RouterLink>
        <RouterLink 
          to="/admin/configuracoes" 
          style={linkStyle("/admin/configuracoes")}
        >
          Configurações
        </RouterLink>

        <h4 style={{...headingStyle, fontSize: '1em', marginTop: '15px', marginBottom: '5px'}}>Relatórios</h4>
        <RouterLink 
          to="/admin/relatorios/vendas" 
          style={linkStyle("/admin/relatorios/vendas")}
        >
          Vendas
        </RouterLink>
        <RouterLink 
          to="/admin/relatorios/produtos" 
          style={linkStyle("/admin/relatorios/produtos")}
        >
          Produtos Vendidos
        </RouterLink>
      </nav>
    </div>
  );
};

export default AdminSidebar;
