import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import GerenciarCategoriasPage from './GerenciarCategoriasPage';
import adminService from '../../services/adminService';

jest.mock('../../services/adminService');

const mockCategorias = [
  { id: 1, nome: 'Pizzas', descricao: 'Pizzas de todos os sabores' },
  { id: 2, nome: 'Bebidas', descricao: 'Refrigerantes, sucos, água' },
];

describe('GerenciarCategoriasPage', () => {
  beforeEach(() => {
    adminService.getCategorias.mockResolvedValue({ data: mockCategorias });
    adminService.createCategoria.mockResolvedValue({ data: { id: 3, nome: 'Nova Categoria', descricao: '' } });
    adminService.updateCategoria.mockResolvedValue({ data: { ...mockCategorias[0], nome: 'Pizzas Salgadas' } });
    adminService.deleteCategoria.mockResolvedValue({});
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('deve renderizar a tabela de categorias com dados mockados', async () => {
    render(<Router><GerenciarCategoriasPage /></Router>);
    expect(screen.getByText(/carregando categorias.../i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Pizzas')).toBeInTheDocument();
      expect(screen.getByText('Bebidas')).toBeInTheDocument();
    });
    expect(adminService.getCategorias).toHaveBeenCalledTimes(1);
  });

  test('deve abrir o modal de formulário ao clicar em "Nova Categoria"', async () => {
    render(<Router><GerenciarCategoriasPage /></Router>);
    await waitFor(() => expect(adminService.getCategorias).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('button', { name: /nova categoria/i }));
    
    expect(await screen.findByRole('heading', { name: /nova categoria/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/nome:/i)).toBeInTheDocument();
  });

  test('deve criar uma nova categoria ao submeter o formulário', async () => {
    render(<Router><GerenciarCategoriasPage /></Router>);
    await waitFor(() => expect(adminService.getCategorias).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('button', { name: /nova categoria/i }));
    await screen.findByRole('heading', { name: /nova categoria/i });

    fireEvent.change(screen.getByLabelText(/nome:/i), { target: { value: 'Sobremesas' } });
    fireEvent.click(screen.getByRole('button', { name: /criar categoria/i }));

    await waitFor(() => {
      expect(adminService.createCategoria).toHaveBeenCalledWith(expect.objectContaining({ nome: 'Sobremesas' }));
      expect(adminService.getCategorias).toHaveBeenCalledTimes(2); // Re-fetch
    });
  });
  
  test('deve excluir uma categoria ao confirmar', async () => {
    window.confirm = jest.fn(() => true);
    render(<Router><GerenciarCategoriasPage /></Router>);
    await waitFor(() => expect(screen.getByText(mockCategorias[0].nome)).toBeInTheDocument());

    const deleteButtons = await screen.findAllByRole('button', { name: /excluir/i });
    fireEvent.click(deleteButtons[0]);

    expect(window.confirm).toHaveBeenCalled();
    await waitFor(() => {
      expect(adminService.deleteCategoria).toHaveBeenCalledWith(mockCategorias[0].id);
      expect(adminService.getCategorias).toHaveBeenCalledTimes(2); // Re-fetch
    });
  });

  // Adicionar testes para:
  // - Edição de categoria (abrir modal com dados, submeter, verificar update)
  // - Validações de formulário (ex: nome obrigatório)
  // - Tratamento de erro ao criar/editar/excluir
});
```
