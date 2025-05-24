import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import CozinhaDashboardPage from './CozinhaDashboardPage';
import cozinhaService from '../../services/cozinhaService';

jest.mock('../../services/cozinhaService');

const mockPedidosCozinha = [
  { 
    id_pedido_origem: 1, tipo_origem: 'Mesa', identificador_cliente: 'Mesa M01', 
    horario_entrada_cozinha: new Date().toISOString(), status_cozinha_atual: 'AguardandoPreparo', 
    itens: [{ nome_produto: 'Pizza Calabresa', quantidade: 1, observacoes_item: 'Sem cebola' }] 
  },
  { 
    id_pedido_origem: 2, tipo_origem: 'WhatsApp', identificador_cliente: '+5511999998888', 
    horario_entrada_cozinha: new Date().toISOString(), status_cozinha_atual: 'EmPreparo', 
    itens: [{ nome_produto: 'Refrigerante', quantidade: 2 }] 
  },
];

describe('CozinhaDashboardPage', () => {
  beforeEach(() => {
    cozinhaService.getPedidosParaPreparar.mockResolvedValue({ data: mockPedidosCozinha });
    cozinhaService.atualizarStatusPedidoCozinha.mockResolvedValue({ data: {} }); // Simula sucesso na atualização
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('deve renderizar o estado de carregamento e depois os cards de pedido', async () => {
    render(<Router><CozinhaDashboardPage /></Router>);
    expect(screen.getByText(/carregando pedidos da cozinha.../i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/pedido: mesa m01/i)).toBeInTheDocument();
      expect(screen.getByText(/pedido: \+5511999998888/i)).toBeInTheDocument();
    });
    expect(cozinhaService.getPedidosParaPreparar).toHaveBeenCalledTimes(1);
  });

  test('deve exibir mensagem se não houver pedidos para preparar', async () => {
    cozinhaService.getPedidosParaPreparar.mockResolvedValueOnce({ data: [] });
    render(<Router><CozinhaDashboardPage /></Router>);

    await waitFor(() => {
      expect(screen.getByText(/nenhum pedido para preparar no momento/i)).toBeInTheDocument();
    });
  });

  test('deve chamar o serviço para atualizar status ao clicar em "Marcar Em Preparo"', async () => {
    render(<Router><CozinhaDashboardPage /></Router>);
    await waitFor(() => expect(screen.getByText(/pedido: mesa m01/i)).toBeInTheDocument());

    // O pedido da Mesa M01 está em 'AguardandoPreparo'
    // Encontrar o botão "Marcar Em Preparo" associado a este card.
    // O PedidoCozinhaCard renderiza o botão. Precisamos de um seletor mais específico se houver muitos.
    // Supondo que é o primeiro botão com este texto.
    const botaoMarcarEmPreparo = screen.getAllByRole('button', { name: /marcar em preparo/i })[0];
    fireEvent.click(botaoMarcarEmPreparo);

    await waitFor(() => {
      expect(cozinhaService.atualizarStatusPedidoCozinha).toHaveBeenCalledWith(
        mockPedidosCozinha[0].tipo_origem,
        mockPedidosCozinha[0].id_pedido_origem,
        'EmPreparo'
      );
      // A página deve re-buscar os pedidos após a atualização
      expect(cozinhaService.getPedidosParaPreparar).toHaveBeenCalledTimes(2); // 1 inicial + 1 após atualização
    });
  });
  
  test('deve chamar o serviço para atualizar status ao clicar em "Marcar Pronto"', async () => {
    render(<Router><CozinhaDashboardPage /></Router>);
    await waitFor(() => expect(screen.getByText(/pedido: \+5511999998888/i)).toBeInTheDocument());

    // O pedido do WhatsApp +5511999998888 está em 'EmPreparo'
    const botaoMarcarPronto = screen.getAllByRole('button', { name: /marcar pronto/i })[0];
    fireEvent.click(botaoMarcarPronto);

    await waitFor(() => {
      expect(cozinhaService.atualizarStatusPedidoCozinha).toHaveBeenCalledWith(
        mockPedidosCozinha[1].tipo_origem,
        mockPedidosCozinha[1].id_pedido_origem,
        'Pronto'
      );
      expect(cozinhaService.getPedidosParaPreparar).toHaveBeenCalledTimes(2);
    });
  });

  test('deve exibir mensagem de erro se a busca de pedidos falhar', async () => {
    cozinhaService.getPedidosParaPreparar.mockRejectedValueOnce(new Error("API Falhou"));
    render(<Router><CozinhaDashboardPage /></Router>);

    await waitFor(() => {
      expect(screen.getByText(/erro ao buscar pedidos. tente atualizar./i)).toBeInTheDocument();
    });
  });

  test('deve re-buscar os pedidos ao clicar no botão "Atualizar Lista"', async () => {
    render(<Router><CozinhaDashboardPage /></Router>);
    await waitFor(() => expect(cozinhaService.getPedidosParaPreparar).toHaveBeenCalledTimes(1));

    const botaoAtualizar = screen.getByRole('button', { name: /atualizar lista/i });
    fireEvent.click(botaoAtualizar);

    await waitFor(() => expect(cozinhaService.getPedidosParaPreparar).toHaveBeenCalledTimes(2));
  });
});

// Outros testes possíveis:
// - Testar a ordenação dos pedidos (se houver lógica de ordenação no frontend, embora o backend já ordene).
// - Testar o feedback de "Atualizando..." no botão enquanto uma ação está em progresso no card.
// - Testar o tratamento de erro dentro do PedidoCozinhaCard ao tentar atualizar status.
```
