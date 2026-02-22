import React, { useState } from "react";
import { Layout, Menu, Avatar, Typography } from "antd";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Lightbulb,
  ShoppingCart,
  Package,
  Settings,
  LogOut,
  User,
  ChefHat,
  ChevronLeft,
} from "lucide-react";
import { UserRole } from "../types";

const { Sider, Content } = Layout;
const { Title, Text } = Typography;

interface MainLayoutProps {
  children: React.ReactNode;
  userRole: UserRole;
  onLogout: () => void;
}

const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  userRole,
  onLogout,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  // Define menu items based on role
  const menuItems = [
    {
      key: "/inventory",
      icon: <Package size={20} />,
      label: "Inventory",
      show: userRole === UserRole.STORE_MANAGER,
    },
    {
      key: "/purchase",
      icon: <ShoppingCart size={20} />,
      label: "Purchase",
      show: userRole === UserRole.STORE_MANAGER,
    },
    {
      key: "/overview",
      icon: <Lightbulb size={20} />,
      label: "Overview",
      show: userRole === UserRole.OPERATION_MANAGER,
    },
    {
      key: "/settings",
      icon: <Settings size={20} />,
      label: "Basic Settings",
      show: userRole === UserRole.OPERATION_MANAGER,
    },
  ].filter((item) => item.show);

  return (
    <Layout className="h-screen overflow-hidden">
      <Sider
        collapsible
        collapsed={collapsed}
        trigger={null}
        theme="light"
        className="border-r border-gray-200 shadow-sm z-10 flex flex-col justify-between"
        width="20vw"
      >
        <div className="flex flex-col flex-1 h-full overflow-hidden">
          {/* Logo Section */}
          <div className="flex items-center gap-3 px-6 py-6 mb-2 shrink-0">
            <div className="w-8 h-8 bg-[#1890ff] rounded flex items-center justify-center shrink-0 shadow-sm">
              <ChefHat className="text-white" size={20} />
            </div>
            {!collapsed && (
              <div className="flex flex-col overflow-hidden transition-all duration-300 ease-in-out">
                <Title
                  level={5}
                  style={{ margin: 0, whiteSpace: "nowrap", fontSize: "16px" }}
                >
                  Ramen Heaven
                </Title>
                <Text
                  type="secondary"
                  style={{ fontSize: "10px" }}
                  className="uppercase tracking-wider"
                >
                  Inventory Management
                </Text>
              </div>
            )}
          </div>

          {/* Menu Section */}
          <div className="flex-1 overflow-y-auto py-2">
            <Menu
              mode="inline"
              selectedKeys={[location.pathname]}
              items={menuItems}
              onClick={({ key }) => navigate(key)}
              style={{ borderRight: 0 }}
              className="px-2 font-medium border-none"
            />
          </div>

          {/* User Profile Section at Bottom */}
          <div className="border-t border-gray-100 p-4 shrink-0 bg-gray-50/50">
            <div
              className={`flex items-center ${collapsed ? "justify-center" : "justify-between"} transition-all`}
            >
              {!collapsed ? (
                <div className="flex items-center gap-3 overflow-hidden">
                  <Avatar
                    style={{ backgroundColor: "#1890ff" }}
                    icon={<User size={16} />}
                    size="default"
                  />
                  <div className="flex flex-col min-w-0">
                    <span className="font-semibold text-sm text-gray-700 truncate">
                      User Name
                    </span>
                    <span className="text-xs text-gray-500 truncate capitalize">
                      {userRole.replace("_", " ").toLowerCase()}
                    </span>
                  </div>
                </div>
              ) : (
                <Avatar
                  style={{ backgroundColor: "#1890ff" }}
                  icon={<User size={16} />}
                  size="small"
                />
              )}

              {!collapsed && (
                <div
                  onClick={onLogout}
                  className="cursor-pointer text-gray-400 hover:text-red-500 transition-colors p-2 rounded-full hover:bg-red-50"
                  title="Logout"
                >
                  <LogOut size={18} />
                </div>
              )}
            </div>
            {collapsed && (
              <div className="mt-4 flex justify-center">
                <div
                  onClick={onLogout}
                  className="cursor-pointer text-gray-400 hover:text-red-500 transition-colors"
                  title="Logout"
                >
                  <LogOut size={16} />
                </div>
              </div>
            )}
          </div>

          {/* Collapse Trigger */}
          <div
            className="border-t border-gray-100 p-3 flex justify-center cursor-pointer hover:bg-gray-100 transition-colors bg-white text-gray-400 hover:text-gray-600"
            onClick={() => setCollapsed(!collapsed)}
          >
            <div
              className={`transition-transform duration-200 ${collapsed ? "rotate-180" : ""}`}
            >
              <ChevronLeft size={16} />
            </div>
          </div>
        </div>
      </Sider>

      <Layout className="bg-[#f0f2f5]">
        <Content className="overflow-y-auto h-full flex flex-col p-6">
          {/* Content */}
          <div className="flex-1">
            <div className="max-w-[1600px] mx-auto">{children}</div>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
