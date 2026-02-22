import React, { useState } from "react";
import { HashRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { ConfigProvider } from "antd";
import MainLayout from "./components/MainLayout";
import InventoryManagement from "./pages/InventoryManagement";
import PurchaseManagement from "./pages/PurchaseManagement";
import BasicSettings from "./pages/BasicSettings";
import Overview from "./pages/Overview";
import Login from "./pages/Login";
import { UserRole } from "./types";

const App: React.FC = () => {
  const [userRole, setUserRole] = useState<UserRole | null>(null);

  const handleLogin = (role: UserRole) => {
    setUserRole(role);
  };

  const handleLogout = () => {
    setUserRole(null);
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#1890ff", // Reference Blue
          borderRadius: 2, // Sharper corners like reference
          fontFamily: "Nunito Sans, sans-serif",
          colorText: "#000000d9",
          colorBgContainer: "#ffffff",
        },
        components: {
          Layout: {
            siderBg: "#ffffff",
            bodyBg: "#f0f2f5",
          },
          Menu: {
            itemSelectedBg: "#e6f7ff",
            itemSelectedColor: "#1890ff",
          },
          Table: {
            headerBg: "#fafafa",
            headerColor: "#000000d9",
            headerSplitColor: "#f0f0f0",
          },
        },
      }}
    >
      <HashRouter>
        <Routes>
          <Route
            path="/login"
            element={
              !userRole ? (
                <Login onLogin={handleLogin} />
              ) : (
                <Navigate
                  to={
                    userRole === UserRole.STORE_MANAGER
                      ? "/inventory"
                      : "/overview"
                  }
                  replace
                />
              )
            }
          />

          {userRole ? (
            <Route
              path="/"
              element={
                <MainLayout userRole={userRole} onLogout={handleLogout}>
                  <Outlet />
                </MainLayout>
              }
            >
              {/* Default Redirects based on role */}
              <Route
                index
                element={
                  <Navigate
                    to={
                      userRole === UserRole.STORE_MANAGER
                        ? "/inventory"
                        : "/overview"
                    }
                    replace
                  />
                }
              />

              <Route path="inventory" element={<InventoryManagement />} />
              <Route path="purchase" element={<PurchaseManagement />} />
              <Route path="settings" element={<BasicSettings />} />
              <Route path="overview" element={<Overview />} />
            </Route>
          ) : (
            <Route path="*" element={<Navigate to="/login" replace />} />
          )}
        </Routes>
      </HashRouter>
    </ConfigProvider>
  );
};

export default App;
