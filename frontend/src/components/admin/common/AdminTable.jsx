import React from 'react';

const AdminTable = ({ columns, data, onEdit, onDelete, customActions }) => {
  if (!columns || !data) {
    return <p>Dados não disponíveis para a tabela.</p>;
  }

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '20px',
    fontSize: '0.9em',
    boxShadow: '0 0 10px rgba(0, 0, 0, 0.05)',
  };

  const thStyle = {
    backgroundColor: '#f8f9fa',
    color: '#495057',
    padding: '12px 15px',
    border: '1px solid #dee2e6',
    textAlign: 'left',
    fontWeight: 'bold',
  };

  const tdStyle = {
    padding: '10px 15px',
    border: '1px solid #e9ecef',
    color: '#212529',
  };
  
  const trStyle = {
    borderBottom: '1px solid #e9ecef',
  };

  const evenRowStyle = {
    ...trStyle,
    // backgroundColor: '#fdfdfe', // Very light alternating row color
  };
  
  const actionButtonStyle = {
    marginRight: '5px',
    padding: '5px 8px',
    fontSize: '0.85em',
    border: '1px solid transparent',
    borderRadius: '4px',
    cursor: 'pointer',
  };

  const editButtonStyle = {
    ...actionButtonStyle,
    backgroundColor: '#ffc107', // Amarelo
    color: '#212529',
  };
  
  const deleteButtonStyle = {
    ...actionButtonStyle,
    backgroundColor: '#dc3545', // Vermelho
    color: 'white',
  };


  return (
    <div style={{ overflowX: 'auto' }}> {/* Para responsividade em telas menores */}
      <table style={tableStyle}>
        <thead>
          <tr style={trStyle}>
            {columns.map((col) => (
              <th key={col.key || col.header} style={thStyle}>{col.header}</th>
            ))}
            {(onEdit || onDelete || customActions) && <th style={thStyle}>Ações</th>}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + ((onEdit || onDelete || customActions) ? 1 : 0)} style={{...tdStyle, textAlign: 'center'}}>
                Nenhum dado encontrado.
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr key={row.id || rowIndex} style={rowIndex % 2 === 0 ? trStyle : evenRowStyle}>
                {columns.map((col) => (
                  <td key={`${col.key || col.header}-${row.id || rowIndex}`} style={tdStyle}>
                    {col.render ? col.render(row) : (row[col.key] !== null && typeof row[col.key] !== 'undefined' ? String(row[col.key]) : 'N/A')}
                  </td>
                ))}
                {(onEdit || onDelete || customActions) && (
                  <td style={tdStyle}>
                    {customActions && customActions.map((action, index) => (
                      <button
                        key={index}
                        onClick={() => action.handler(row)}
                        style={{...actionButtonStyle, ...action.style}}
                        title={action.label}
                      >
                        {action.label}
                      </button>
                    ))}
                    {onEdit && (
                      <button onClick={() => onEdit(row)} style={editButtonStyle} title="Editar">
                        Editar
                      </button>
                    )}
                    {onDelete && (
                      <button onClick={() => onDelete(row.id || row.chave)} style={deleteButtonStyle} title="Excluir">
                        Excluir
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default AdminTable;
