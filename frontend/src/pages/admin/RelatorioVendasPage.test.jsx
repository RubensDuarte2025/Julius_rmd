import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import RelatorioVendasPage from './RelatorioVendasPage';
import adminService from '../../services/adminService';

jest.mock('../../services/adminService');

const mockVendasData = [
  { id_pagamento: 1, id_pedido_origem: 101, origem_pedido: 'Mesa', data_pagamento: new Date().toISOString(), valor_pago: '55.50', metodo_pagamento: 'Dinheiro' },
  { id_pagamento: 2, id_pedido_origem: 202, origem_pedido: 'WhatsApp', data_pagamento: new Date().toISOString(), valor_pago: '30.00', metodo_pagamento: 'PIX' },
];

describe('RelatorioVendasPage', () => {
  beforeEach(() => {
    adminService.getRelatorioVendas.mockResolvedValue({ data: mockVendasData });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('deve renderizar o formulário de filtro e a tabela de vendas', async () => {
    render(<Router><RelatorioVendasPage /></Router>);

    expect(screen.getByLabelText(/data início/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/data fim/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /gerar relatório/i })).toBeInTheDocument();

    // Inicialmente, a tabela pode estar vazia ou exibir algo se houver um fetch inicial.
    // No componente atual, o fetch é feito ao clicar no botão.
    // Vamos simular o clique para carregar os dados.
    fireEvent.change(screen.getByLabelText(/data início/i), { target: { value: '2023-01-01' } });
    fireEvent.change(screen.getByLabelText(/data fim/i), { target: { value: '2023-01-31' } });
    fireEvent.click(screen.getByRole('button', { name: /gerar relatório/i }));

    await waitFor(() => {
      // Verificar se a tabela foi renderizada com os dados mockados
      expect(screen.getByText('R$ 55.50')).toBeInTheDocument(); // Parte do valor formatado
      expect(screen.getByText('R$ 30.00')).toBeInTheDocument();
      expect(screen.getByText('Mesa')).toBeInTheDocument();
      expect(screen.getByText('WhatsApp')).toBeInTheDocument();
    });
    expect(adminService.getRelatorioVendas).toHaveBeenCalledTimes(1);
    expect(adminService.getRelatorioVendas).toHaveBeenCalledWith({ data_inicio: '2023-01-01', data_fim: '2023-01-31' });
  });

  test('deve exibir mensagem de erro se a busca de relatório falhar', async () => {
    adminService.getRelatorioVendas.mockRejectedValueOnce(new Error("API Falhou"));
    render(<Router><RelatorioVendasPage /></Router>);

    fireEvent.change(screen.getByLabelText(/data início/i), { target: { value: '2023-01-01' } });
    fireEvent.change(screen.getByLabelText(/data fim/i), { target: { value: '2023-01-31' } });
    fireEvent.click(screen.getByRole('button', { name: /gerar relatório/i }));

    await waitFor(() => {
      expect(screen.getByText(/falha ao carregar relatório de vendas/i)).toBeInTheDocument();
    });
  });
  
  test('deve exibir alerta se datas não forem preenchidas ao clicar em gerar relatório', () => {
    // Mock da função window.alert
    window.alert = jest.fn();
    render(<Router><RelatorioVendasPage /></Router>);

    fireEvent.click(screen.getByRole('button', { name: /gerar relatório/i }));
    
    expect(window.alert).toHaveBeenCalledWith("Por favor, selecione data de início e data de fim.");
    expect(adminService.getRelatorioVendas).not.toHaveBeenCalled();
    
    // Limpar o mock para outros testes
    window.alert.mockClear();
  });

  // Adicionar mais testes para:
  // - Diferentes combinações de filtros de data.
  // - Relatório sem vendas (lista vazia).
  // - Formatação correta dos dados na tabela (data, valor).
  // - Cálculo do total de vendas no período.
});
```
