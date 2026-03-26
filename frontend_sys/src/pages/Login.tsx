import React from "react";
import { Typography } from "antd";
import { UserRole } from "../types";
import { ChefHat } from "lucide-react";

const { Title, Text } = Typography;

interface LoginProps {
  onLogin: (role: UserRole) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md shadow-xl border-0 bg-white rounded-xl p-8">
        <div className="flex flex-col items-center mb-10">
          <div className="w-16 h-16 bg-orange-500 rounded-xl flex items-center justify-center mb-5 shadow-sm">
            <ChefHat className="text-white" size={40} />
          </div>
          <Title level={2} style={{ marginBottom: 0 }}>
            Ramen Heaven
          </Title>
          <Text type="secondary" className="mt-1">
            Inventory Management Portal
          </Text>
        </div>

        <div className="space-y-4">
          <div
            className="p-5 bg-blue-50 rounded-lg border border-blue-100 hover:border-blue-300 transition-all cursor-pointer hover:shadow-md"
            onClick={() => onLogin(UserRole.STORE_MANAGER)}
          >
            <div className="font-bold text-blue-900 text-lg mb-0.5">
              Store Manager
            </div>
            <div className="text-blue-600/80 text-sm">
              Access to Inventory Counting & Purchasing
            </div>
          </div>

          <div
            className="p-5 bg-purple-50 rounded-lg border border-purple-100 hover:border-purple-300 transition-all cursor-pointer hover:shadow-md"
            onClick={() => onLogin(UserRole.OPERATION_MANAGER)}
          >
            <div className="font-bold text-purple-900 text-lg mb-0.5">
              Operation Manager
            </div>
            <div className="text-purple-600/80 text-sm">
              Access to Settings, Data & Master Records
            </div>
          </div>
        </div>

        <div className="mt-10 text-center text-xs text-gray-400 font-medium">
          v1.0.0 MVP Build
        </div>
      </div>
    </div>
  );
};

export default Login;
