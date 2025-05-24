# Pizzeria SaaS - System Architecture

This document outlines the system architecture for the Pizzeria SaaS platform.

## 1. Chosen Technology Stack

The following technology stack has been preliminarily chosen, with rationale for each choice:

*   **Backend Programming Language:**
    *   **Python (with Django):** Chosen for its rapid development capabilities, extensive libraries (beneficial for integrations like WhatsApp Business API), and suitability for building REST APIs. Django's "batteries-included" nature helps in quick setup of admin panels and ORM.
*   **Frontend Framework (for admin, attendant, kitchen panels):**
    *   **React.js:** Selected due to its large community, component-based architecture, and strong ecosystem, making it ideal for developing Single Page Applications (SPAs) for the internal panels.
*   **Database:**
    *   **PostgreSQL:** Chosen for its robustness, ACID compliance, advanced features, and strong performance with structured relational data, which aligns well with the needs of managing orders, customers, and products.
*   **Cloud Services Provider:**
    *   **AWS (Amazon Web Services):** Preferred for its mature and comprehensive suite of services (e.g., EC2 for application servers, RDS for PostgreSQL, S3 for static files/media, SQS for message queues, ElastiCache for Redis).
*   **Cache:**
    *   **Redis:** Selected for its high performance as an in-memory data store, suitable for caching sessions, frequently accessed query results, and other ephemeral data.
*   **Message Queues (for asynchronous processing):**
    *   **RabbitMQ or AWS SQS:** Chosen to decouple services and handle background tasks like sending notifications, processing bulk operations, etc. AWS SQS is a strong contender if fully within the AWS ecosystem.

## 2. General System Architecture Design

*   **Software Architecture:**
    *   **Monolithic with Clear Modules (for MVP):** The system will initially be developed as a monolith using Django. This approach simplifies development and deployment for the MVP. Logical separation will be maintained through distinct Django apps representing the core modules: `whatsapp_orders`, `table_service`, `kitchen`, `payments`, `administration`, `users`, `products`.
    *   **Future Evolution to Microservices:** While the MVP is monolithic, the design will keep in mind a potential future migration to a microservices architecture as the system scales and requires more independent component scalability and development.
*   **APIs:**
    *   **Internal RESTful API:** A comprehensive RESTful API will be developed using Django (e.g., with Django REST Framework) to facilitate communication between the React frontend and the Django backend.
    *   **WhatsApp Integration API:** The system will integrate with a WhatsApp Business Solution Provider (BSP) like Twilio. The backend will expose necessary endpoints to receive messages from the BSP and send replies.
    *   **Payment Gateway APIs:** Integrations with APIs from PIX providers and credit card gateways will be implemented for payment processing.
*   **Real-time Communication:**
    *   **WebSockets (e.g., Django Channels):** WebSockets will be used for features requiring real-time updates, such as the kitchen display screen (new orders, status changes) and potentially live updates on attendant panels. Django Channels is the preferred library for integrating WebSocket capabilities within the Django framework.

## 3. WhatsApp Communication Architecture

*   **Strategy:** Utilize a **Business Solution Provider (BSP) for WhatsApp, such as Twilio.**
*   **Rationale:** This approach is chosen for the MVP to:
    *   Accelerate development by leveraging the BSP's existing infrastructure and SDKs.
    *   Simplify compliance with WhatsApp's policies.
    *   Reduce the operational overhead of managing a direct WhatsApp Business API integration.
*   **Mechanism:** The Django backend will communicate with the chosen BSP's API (e.g., Twilio API for WhatsApp) to send and receive messages. Webhooks provided by the BSP will be configured to forward incoming WhatsApp messages to specific endpoints on our backend.

## 4. Conceptual Architecture Diagram (Description)

*   **Users:**
    *   **Customers (via WhatsApp):** Interact with the system by sending messages to the Pizzeria's WhatsApp number.
    *   **Internal Users (Attendants, Kitchen Staff, Administrators):** Interact with the system via web-based frontend panels (React).
*   **Communication Channels & Frontend:**
    *   **WhatsApp Channel:** Customer messages are routed via a BSP (e.g., Twilio) to the Backend.
    *   **Frontend Application (React.js):** Single Page Application providing interfaces for internal users. It communicates with the Backend via the internal RESTful API and receives real-time updates via WebSockets.
*   **Backend System (Python/Django):**
    *   **Application Server (e.g., Gunicorn behind Nginx):** Hosts the Django application.
    *   **Core Logic & Modules:** Implements all business rules, order processing, user management, etc., structured into Django apps.
    *   **API Endpoints:**
        *   RESTful API for frontend communication.
        *   Webhook endpoints for receiving data from WhatsApp BSP.
        *   Endpoints for interacting with payment gateways.
    *   **Real-time Component (Django Channels):** Manages WebSocket connections for live updates to the frontend.
*   **Data Storage & Caching:**
    *   **Database (PostgreSQL on AWS RDS):** Primary persistent storage for all application data (orders, users, products, etc.).
    *   **Cache (Redis on AWS ElastiCache):** Used for session management, caching frequently accessed data to improve performance.
*   **Asynchronous Processing:**
    *   **Message Queue (AWS SQS or RabbitMQ):** Handles background tasks such as sending email/SMS confirmations, generating reports, or other long-running processes, ensuring the main application threads remain responsive.
*   **External Services:**
    *   **WhatsApp Business Solution Provider (e.g., Twilio):** Manages WhatsApp message transit to and from the backend.
    *   **Payment Gateways:** External services for processing PIX and credit/debit card payments.
    *   **AWS Services:** Foundational cloud infrastructure (compute, database hosting, storage, etc.).

This architecture aims to provide a scalable, maintainable, and robust platform for the Pizzeria SaaS, starting with an MVP that can be evolved over time.
