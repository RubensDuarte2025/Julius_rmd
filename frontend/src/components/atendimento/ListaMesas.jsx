import React, { useState, useEffect, useCallback } from 'react';
import atendimentoService from '../../services/atendimentoService';
import MesaCard from './MesaCard';

const ListaMesas = () => {
  const [mesas, setMesas] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMesas = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await atendimentoService.getMesas();
      setMesas(response.data || []); // response.data should be the array of mesas
    } catch (err) {
      console.error("Erro ao buscar mesas:", err);
      setError("Falha ao carregar mesas. Tente novamente.");
      setMesas([]); // Limpa mesas em caso de erro
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMesas();
  }, [fetchMesas]);

  const containerStyle = {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'center',
    padding: '20px',
  };

  const controlStyle = {
    width: '100%',
    textAlign: 'center',
    marginBottom: '20px',
  };

  if (isLoading) {
    return <p style={controlStyle}>Carregando mesas...</p>;
  }

  if (error) {
    return (
      <div style={controlStyle}>
        <p style={{ color: 'red' }}>{error}</p>
        <button onClick={fetchMesas}>Tentar Novamente</button>
      </div>
    );
  }

  if (mesas.length === 0) {
    return (
        <div style={controlStyle}>
            <p>Nenhuma mesa encontrada.</p>
            <button onClick={fetchMesas}>Atualizar Lista</button>
        </div>
    );
  }

  return (
    <div>
      <div style={controlStyle}>
        <button onClick={fetchMesas} disabled={isLoading}>
          {isLoading ? 'Atualizando...' : 'Atualizar Lista de Mesas'}
        </button>
      </div>
      <div style={containerStyle}>
        {mesas.map((mesa) => (
          <MesaCard key={mesa.id} mesa={mesa} />
        ))}
      </div>
    </div>
  );
};

export default ListaMesas;
