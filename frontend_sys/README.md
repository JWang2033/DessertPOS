# Ramen Heaven Inventory & Purchase System

A modern, React-based inventory and purchase order management system for the Ramen Heaven restaurant chain. This application allows store managers and administrators to track stock levels, manage purchase orders, and visualize inventory health across multiple locations.

## Features

### 📊 Overview Dashboard
- **Key Metrics**: Real-time stats on total inventory items, low stock alerts, and stock accuracy.
- **Cross-Store Visualization**: View inventory status across the entire network.
- **Dynamic Grouping**: Group items by Store, Health Status, or Accuracy for better insights.

### 📦 Inventory Management
- **Detailed Tracking**: Monitor ingredient and semi-finished product quantities.
- **Smart Filtering**: Filter by Location (Store ID) and Item Type.
- **Status Indicators**: Visual badges for "Sufficient" vs "Restock Needed" items.
- **Edit Mode**: Quickly update actual quantities and see variance percentages.

### 📝 Purchase Order Management
- **Create Orders**: Easy-to-use drawer interface for creating new purchase orders.
- **Automatic Calculations**: Real-time calculation of line item totals and order grand totals.
- **Order History**: View and filter past purchase orders by date or store.
- **Print-Ready View**: Clean, read-only view of purchase order details.

### ⚙️ Settings
- **Basic Configuration**: Manage application settings.

## Tech Stack

- **Framework**: [React 19](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **UI Component Library**: [Ant Design (v6)](https://ant.design/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Routing**: [React Router DOM](https://reactrouter.com/)
- **Utilities**: `dayjs` for date formatting.

## Project Structure

```bash
src/
├── components/         # Reusable UI components
│   ├── CreateOrderDrawer.tsx       # Form for new POs
│   ├── PurchaseOrderDetailsDrawer.tsx # Read-only PO view
│   ├── InventoryToolbar.tsx        # Shared search/filter toolbar
│   └── ...
├── pages/              # Main route views
│   ├── Overview.tsx                # Dashboard
│   ├── InventoryManagement.tsx     # Inventory list & edit
│   ├── PurchaseManagement.tsx      # PO list & management
│   └── ...
├── services/           # Mock data and API services
├── utils/              # Shared helper functions
└── types.ts            # TypeScript definitions
```

## Getting Started

1.  **Install Dependencies**
    ```bash
    npm install
    ```

2.  **Run Development Server**
    ```bash
    npm run dev
    ```

3.  **Build for Production**
    ```bash
    npm run build
    ```

## Development Guide

### Adding New Features

1.  **Define Types**: Add any new data interfaces to `src/types.ts`.
2.  **Create Components**: Build reusable UI parts in `src/components/`. Use Ant Design components where possible to maintain consistency.
3.  **Create Page**: If a new view is needed, create it in `src/pages/`.
4.  **Add Route**: Register the new route in `src/App.tsx`.

### Code Style & Best Practices

- **Functional Components**: Use React Functional Components with Hooks.
- **Type Safety**: Avoid `any` types; define interfaces for props and state.
- **Styling**: use Tailwind CSS utility classes and Ant Design's `style` prop or tokens for theming.
