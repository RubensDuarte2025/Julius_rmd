# Pizzeria SaaS - Database Schema (PostgreSQL)

This document outlines the main entities and their attributes for the Pizzeria SaaS platform's PostgreSQL database.

## Core Entities

### 1. `Papeis` (Roles)
Stores different user roles within the system.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the role.
*   `nome_papel` (VARCHAR(50) UNIQUE NOT NULL): Name of the role (e.g., Admin, Atendente, Cozinheiro).

### 2. `Usuarios` (Users)
Stores information about internal system users.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the user.
*   `nome` (VARCHAR(255) NOT NULL): Full name of the user.
*   `email` (VARCHAR(255) UNIQUE NOT NULL): Email address of the user (used for login).
*   `senha_hash` (VARCHAR(255) NOT NULL): Hashed password for the user.
*   `papel_id` (INTEGER NOT NULL, REFERENCES `Papeis`(id)): Foreign key linking to the user's role.
*   `data_criacao` (TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP): Date and time when the user account was created.

### 3. `Clientes` (Customers)
Stores information about pizzeria customers.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the customer.
*   `nome` (VARCHAR(255) NOT NULL): Name of the customer.
*   `telefone` (VARCHAR(20) UNIQUE NOT NULL): Customer's phone number (especially important for WhatsApp orders).
*   `endereco_entrega` (TEXT): Default delivery address (can be expanded into a separate Addresses table if multiple addresses per customer are needed).
*   `data_cadastro` (TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP): Date and time when the customer was registered.
*   *Note: Could be linked to `Usuarios` if customers can also log in, or kept separate for simplicity for WhatsApp-first customers.*

### 4. `CategoriasProdutos` (Product Categories)
Stores categories for organizing products.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the category.
*   `nome` (VARCHAR(100) NOT NULL): Name of the category (e.g., Pizzas Salgadas, Pizzas Doces, Bebidas).
*   `descricao` (TEXT): Optional description of the category.

### 5. `Produtos` (Products)
Stores information about the products offered by the pizzeria.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the product.
*   `categoria_id` (INTEGER NOT NULL, REFERENCES `CategoriasProdutos`(id)): Foreign key linking to the product's category.
*   `nome` (VARCHAR(255) NOT NULL): Name of the product.
*   `descricao` (TEXT): Detailed description of the product.
*   `preco_base` (DECIMAL(10, 2) NOT NULL): Base price of the product.
*   `foto_url` (VARCHAR(2048)): URL for the product's photo.
*   `disponivel` (BOOLEAN DEFAULT TRUE): Whether the product is currently available.
*   `tempo_preparo_estimado` (INTERVAL): Estimated preparation time (e.g., '20 minutes').

### 6. `Ingredientes` (Ingredients)
Stores information about ingredients, mainly for customization purposes.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the ingredient.
*   `nome` (VARCHAR(100) NOT NULL): Name of the ingredient.
*   `custo_adicional` (DECIMAL(10, 2) DEFAULT 0.00): Additional cost if this ingredient is added as an extra.

### 7. `ProdutosIngredientes` (Product Ingredients - Junction Table)
Defines the standard ingredients for each product.
*   `produto_id` (INTEGER NOT NULL, REFERENCES `Produtos`(id)): Foreign key to Products.
*   `ingrediente_id` (INTEGER NOT NULL, REFERENCES `Ingredientes`(id)): Foreign key to Ingredients.
*   `quantidade_padrao` (VARCHAR(100)): Standard quantity or description (e.g., "100g", "1 fatia").
*   PRIMARY KEY (`produto_id`, `ingrediente_id`)

### 8. `Mesas` (Tables)
Stores information about tables in the pizzeria for internal table service.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the table.
*   `numero_mesa` (VARCHAR(10) UNIQUE NOT NULL): Table number or identifier.
*   `status` (VARCHAR(50) NOT NULL DEFAULT 'Livre'): Current status of the table (e.g., Livre, Ocupada, AguardandoPagamento).
*   `capacidade` (INTEGER): Seating capacity of the table.

### 9. `Pedidos` (Orders)
Stores information about customer orders.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the order.
*   `cliente_id` (INTEGER, REFERENCES `Clientes`(id)): Foreign key to the customer who placed the order (nullable if anonymous or table order without prior customer registration).
*   `mesa_id` (INTEGER, REFERENCES `Mesas`(id)): Foreign key to the table if it's a table service order (nullable).
*   `tipo_pedido` (VARCHAR(50) NOT NULL): Type of order (e.g., WhatsApp, Mesa).
*   `status_pedido` (VARCHAR(50) NOT NULL DEFAULT 'Recebido'): Current status of the order (e.g., Recebido, EmPreparo, Pronto, Entregue, Cancelado, Pago).
*   `data_hora_pedido` (TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP): Date and time when the order was placed.
*   `valor_total` (DECIMAL(10, 2) NOT NULL DEFAULT 0.00): Total value of the order.
*   `endereco_entrega_id` (INTEGER, REFERENCES `Enderecos`(id) - *assuming a separate Enderecos table if needed*): Delivery address for WhatsApp orders. For simplicity, `endereco_entrega` (TEXT) could be directly in `Pedidos` if only one address per order is stored.
*   `observacoes` (TEXT): General observations for the order.

### 10. `ItensPedido` (Order Items)
Stores details of each item within an order.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the order item.
*   `pedido_id` (INTEGER NOT NULL, REFERENCES `Pedidos`(id) ON DELETE CASCADE): Foreign key to the order.
*   `produto_id` (INTEGER NOT NULL, REFERENCES `Produtos`(id)): Foreign key to the product.
*   `quantidade` (INTEGER NOT NULL DEFAULT 1): Quantity of this product ordered.
*   `preco_unitario` (DECIMAL(10, 2) NOT NULL): Price of the product at the time of order (could differ from `Produtos.preco_base` if promotions or dynamic pricing apply).
*   `subtotal` (DECIMAL(10, 2) NOT NULL): Calculated subtotal for this item (`quantidade` * `preco_unitario` + customization costs).
*   `observacoes_item` (TEXT): Observations specific to this item in the order.

### 11. `ItensPedidoCustomizacao` (Order Item Customizations)
Stores customizations for an order item (e.g., extra or removed ingredients).
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the customization entry.
*   `item_pedido_id` (INTEGER NOT NULL, REFERENCES `ItensPedido`(id) ON DELETE CASCADE): Foreign key to the specific order item being customized.
*   `ingrediente_id` (INTEGER NOT NULL, REFERENCES `Ingredientes`(id)): Foreign key to the ingredient being added/modified.
*   `quantidade_adicional` (INTEGER DEFAULT 1): Quantity of the ingredient being added (can be negative for removal, though this might be better handled by a specific 'removed' flag or type).
*   `custo_adicional_customizacao` (DECIMAL(10, 2) DEFAULT 0.00): Additional cost for this specific customization (e.g., cost of an extra ingredient).

### 12. `Pagamentos` (Payments)
Stores information related to payments for orders.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the payment.
*   `pedido_id` (INTEGER NOT NULL, REFERENCES `Pedidos`(id)): Foreign key to the order being paid.
*   `metodo_pagamento` (VARCHAR(50) NOT NULL): Payment method used (e.g., PIX, CartaoCredito, CartaoDebito, Dinheiro).
*   `valor_pago` (DECIMAL(10, 2) NOT NULL): Amount paid.
*   `status_pagamento` (VARCHAR(50) NOT NULL DEFAULT 'Pendente'): Status of the payment (e.g., Pendente, Aprovado, Recusado, Reembolsado).
*   `data_hora_pagamento` (TIMESTAMP WITH TIME ZONE): Date and time when the payment was processed.
*   `transacao_id_gateway` (VARCHAR(255)): Transaction ID from the payment gateway, if applicable.
*   `qr_code_pix` (TEXT): The actual QR code data for PIX payments, or a link to it.
*   `link_pagamento_cartao` (VARCHAR(2048)): Link for card payment, if generated by a gateway.

### 13. `ConfiguracoesSistema` (System Configurations)
Stores system-wide configurations and settings.
*   `id` (SERIAL PRIMARY KEY): Unique identifier for the configuration entry.
*   `chave` (VARCHAR(100) UNIQUE NOT NULL): The configuration key (e.g., `taxa_entrega`, `horario_funcionamento_inicio`, `horario_funcionamento_fim`, `mensagem_saudacao_whatsapp`).
*   `valor` (TEXT NOT NULL): The value for the configuration key.

This schema provides a foundational structure. Relationships, constraints (like NOT NULL, UNIQUE), and data types are specified. Indexing strategies would be determined later based on query patterns for performance optimization.
