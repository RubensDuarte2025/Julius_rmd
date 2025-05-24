import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter as Router } from 'react-router-dom'; // Para Modals com Links, etc.
import GerenciarProdutosPage from './GerenciarProdutosPage';
import adminService from '../../services/adminService';

// Mock do adminService
jest.mock('../../services/adminService');

const mockProdutos = [
  { id: 1, nome: 'Pizza Calabresa', categoria_id: 1, categoria_nome: 'Pizzas Salgadas', preco_base: '30.00', disponivel: true },
  { id: 2, nome: 'Refrigerante Lata', categoria_id: 2, categoria_nome: 'Bebidas', preco_base: '5.00', disponivel: true },
];

const mockCategorias = [
  { id: 1, nome: 'Pizzas Salgadas', descricao: 'Pizzas com recheio salgado' },
  { id: 2, nome: 'Bebidas', descricao: 'Refrigerantes, sucos, água' },
];

describe('GerenciarProdutosPage', () => {
  beforeEach(() => {
    adminService.getProductos.mockResolvedValue({ data: mockProdutos });
    adminService.getCategorias.mockResolvedValue({ data: mockCategorias });
    adminService.createProducto.mockResolvedValue({ data: { id: 3, nome: 'Nova Pizza', ...mockProdutos[0] } }); // Simula resposta da criação
    adminService.updateProducto.mockResolvedValue({ data: { ...mockProdutos[0], nome: 'Pizza Calabresa Editada' } });
    adminService.deleteProducto.mockResolvedValue({}); // Geralmente não retorna conteúdo
  });

  afterEach(() => {
    jest.clearAllMocks(); // Limpa os mocks entre os testes
  });

  test('deve renderizar a tabela de produtos com dados mockados', async () => {
    render(<Router><GerenciarProdutosPage /></Router>);

    expect(screen.getByText(/carregando produtos e categorias.../i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Pizza Calabresa')).toBeInTheDocument();
      expect(screen.getByText('Refrigerante Lata')).toBeInTheDocument();
    });
    expect(adminService.getProductos).toHaveBeenCalledTimes(1);
    expect(adminService.getCategorias).toHaveBeenCalledTimes(1);
  });

  test('deve abrir o modal de formulário ao clicar em "Novo Produto"', async () => {
    render(<Router><GerenciarProdutosPage /></Router>);
    await waitFor(() => expect(adminService.getProductos).toHaveBeenCalled()); // Espera carregar

    fireEvent.click(screen.getByRole('button', { name: /novo produto/i }));
    
    // O modal é identificado pelo título. O título é "Novo Produto"
    expect(await screen.findByRole('heading', { name: /novo produto/i })).toBeInTheDocument();
    // Verificar se campos do formulário estão presentes
    expect(screen.getByLabelText(/nome:/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/preço base/i)).toBeInTheDocument();
  });

  test('deve criar um novo produto ao submeter o formulário', async () => {
    render(<Router><GerenciarProdutosPage /></Router>);
    await waitFor(() => expect(adminService.getProductos).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('button', { name: /novo produto/i }));
    await screen.findByRole('heading', { name: /novo produto/i }); // Espera modal

    // Preencher formulário
    fireEvent.change(screen.getByLabelText(/nome:/i), { target: { value: 'Pizza Nova Teste' } });
    fireEvent.change(screen.getByLabelText(/preço base/i), { target: { value: '33.50' } });
    fireEvent.change(screen.getByLabelText(/categoria:/i), { target: { value: mockCategorias[0].id.toString() } }); // Seleciona "Pizzas Salgadas"
    
    // Submeter formulário (o botão de submit dentro do modal)
    // O botão pode ter texto "Criar Produto"
    fireEvent.click(screen.getByRole('button', { name: /criar produto/i }));

    await waitFor(() => {
      expect(adminService.createProducto).toHaveBeenCalledTimes(1);
      // Verificar se os dados corretos foram enviados (exemplo parcial)
      expect(adminService.createProducto).toHaveBeenCalledWith(
        expect.objectContaining({
          nome: 'Pizza Nova Teste',
          preco_base: 33.50,
          categoria_id: mockCategorias[0].id,
        })
      );
    });
    // Verificar se a lista é atualizada (getProductos é chamado novamente)
    // O fetchProdutosECategorias é chamado após submit bem sucedido.
    // O primeiro getProdutos foi no setup, o segundo após o submit.
    await waitFor(() => expect(adminService.getProductos).toHaveBeenCalledTimes(2)); 
  });

  test('deve abrir o modal de edição com dados do produto ao clicar em "Editar"', async () => {
    render(<Router><GerenciarProdutosPage /></Router>);
    await waitFor(() => expect(screen.getByText(mockProdutos[0].nome)).toBeInTheDocument());

    // Encontrar o botão de Editar para o primeiro produto.
    // AdminTable pode renderizar botões de Editar para cada linha.
    // Supondo que o botão de editar tenha um texto acessível ou aria-label.
    // Se AdminTable usa o nome/id para diferenciar, podemos precisar de uma forma mais específica de selecionar.
    // Para este exemplo, vamos assumir que há um botão "Editar" na linha do mockProdutos[0].
    // Esta é uma simplificação; um seletor mais robusto seria screen.getAllByRole('button', {name: /editar/i})[0]
    // ou um data-testid no botão de editar da linha.
    const editButtons = await screen.findAllByRole('button', { name: /editar/i });
    fireEvent.click(editButtons[0]); // Clica no primeiro botão "Editar"

    expect(await screen.findByRole('heading', { name: /editar produto/i })).toBeInTheDocument();
    // Verificar se o formulário está preenchido com os dados do mockProdutos[0]
    expect(screen.getByLabelText(/nome:/i)).toHaveValue(mockProdutos[0].nome);
    expect(screen.getByLabelText(/preço base/i)).toHaveValue(mockProdutos[0].preco_base.toString());
  });
  
  test('deve excluir um produto ao confirmar a exclusão', async () => {
    // Mock da função window.confirm
    window.confirm = jest.fn(() => true); 
    
    render(<Router><GerenciarProdutosPage /></Router>);
    await waitFor(() => expect(screen.getByText(mockProdutos[0].nome)).toBeInTheDocument());

    const deleteButtons = await screen.findAllByRole('button', { name: /excluir/i });
    fireEvent.click(deleteButtons[0]); // Clica no primeiro botão "Excluir"

    expect(window.confirm).toHaveBeenCalledTimes(1); // Verifica se a confirmação foi chamada

    await waitFor(() => {
      expect(adminService.deleteProducto).toHaveBeenCalledWith(mockProdutos[0].id);
      expect(adminService.deleteProducto).toHaveBeenCalledTimes(1);
    });
    // Verificar se a lista é atualizada (getProductos é chamado novamente)
    await waitFor(() => expect(adminService.getProductos).toHaveBeenCalledTimes(2));
  });

});

// Mais testes a serem considerados:
// - Validação de formulário (campos obrigatórios, formato de preço).
// - Comportamento do formulário ao tentar submeter dados inválidos.
// - Atualização de um produto (semelhante à criação, mas chamando updateProducto).
// - Feedback ao usuário (mensagens de sucesso/erro após operações CRUD).
// - Paginação da tabela (se implementada).
// - Filtros ou busca na tabela (se implementada).
```
