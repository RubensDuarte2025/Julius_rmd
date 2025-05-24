import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter as Router } from 'react-router-dom'; // Para Link/Navigate
import MesasDashboardPage from './MesasDashboardPage'; // Ajuste o caminho se necessário
import atendimentoService from '../../services/atendimentoService';

// Mock do serviço
// jest.mock('../../services/atendimentoService'); // Sintaxe Jest
// Para Vitest, o mock é geralmente feito no arquivo de setup ou no topo do teste com vi.mock
// Por simplicidade e compatibilidade de sintaxe com o exemplo, vou usar jest.mock
// mas em um projeto Vitest puro, seria:
// import { vi } from 'vitest';
// vi.mock('../../services/atendimentoService');

jest.mock('../../services/atendimentoService', () => ({
  getMesas: jest.fn(),
  // Adicione outros métodos mockados do atendimentoService se MesasDashboardPage os usar diretamente
}));


const mockMesas = [
  { id: 1, numero_identificador: 'M01', status: 'Livre', pedidos_recentes: [] }, // Ajustado para corresponder ao MesaCard
  { id: 2, numero_identificador: 'M02', status: 'Ocupada', pedidos_recentes: [{ id: 101 }] },
];

describe('MesasDashboardPage', () => {
  beforeEach(() => {
    // Resetar mocks antes de cada teste
    atendimentoService.getMesas.mockResolvedValue({ data: mockMesas });
  });

  test('renders loading state initially and then mesas', async () => {
    render(
      <Router>
        <MesasDashboardPage />
      </Router>
    );
    // O texto "Carregando mesas..." é do componente ListaMesas, que é renderizado por MesasDashboardPage
    expect(screen.getByText(/carregando mesas.../i)).toBeInTheDocument();
    
    await waitFor(() => {
      // MesaCard renderiza "Mesa {numero_identificador}"
      expect(screen.getByText('Mesa M01')).toBeInTheDocument();
      expect(screen.getByText('Mesa M02')).toBeInTheDocument();
    });
    expect(atendimentoService.getMesas).toHaveBeenCalledTimes(1);
  });

  test('renders "nenhuma mesa" message if no mesas are returned', async () => {
    atendimentoService.getMesas.mockResolvedValueOnce({ data: [] });
    render(
      <Router>
        <MesasDashboardPage />
      </Router>
    );
    // O texto "Nenhuma mesa encontrada." é do componente ListaMesas
    await waitFor(() => {
      expect(screen.getByText(/nenhuma mesa encontrada/i)).toBeInTheDocument();
    });
  });

  test('calls getMesas when "Atualizar Lista de Mesas" is clicked', async () => {
    render(
      <Router>
        <MesasDashboardPage />
      </Router>
    );
    await waitFor(() => expect(screen.getByText('Mesa M01')).toBeInTheDocument()); // Esperar carregar inicial

    atendimentoService.getMesas.mockClear(); // Limpar chamadas anteriores
    atendimentoService.getMesas.mockResolvedValueOnce({ data: [mockMesas[0]] }); // Simular uma atualização

    // O botão de atualizar está em ListaMesas
    fireEvent.click(screen.getByRole('button', { name: /atualizar lista de mesas/i }));
    expect(screen.getByText(/carregando mesas.../i)).toBeInTheDocument(); // Mostra loading de novo

    await waitFor(() => {
      expect(atendimentoService.getMesas).toHaveBeenCalledTimes(1);
      // Verificar se a lista foi atualizada (ex: Mesa M02 não está mais lá)
      expect(screen.queryByText('Mesa M02')).not.toBeInTheDocument();
      expect(screen.getByText('Mesa M01')).toBeInTheDocument(); // A Mesa M01 ainda deve estar lá
    });
  });

  test('displays error message if getMesas fails', async () => {
    const errorMessage = "Falha ao carregar mesas. Tente novamente.";
    atendimentoService.getMesas.mockRejectedValueOnce(new Error("API Error"));
    render(
      <Router>
        <MesasDashboardPage />
      </Router>
    );
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
});

// Nota: Os textos exatos como "Carregando mesas...", "Nenhuma mesa encontrada."
// vêm do componente ListaMesas.jsx. Este teste está, na prática, testando
// a integração de MesasDashboardPage com ListaMesas e o serviço mockado.
```
