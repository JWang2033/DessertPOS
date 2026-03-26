import React, { useEffect, useMemo, useState } from "react";
import { Button, Input, Typography, message } from "antd";
import { Plus, Search } from "lucide-react";
import { Ingredient, Category, SemiFinishedProduct, Unit } from "../types";
import {
  batchCreateIngredients,
  createCategory,
  createProduct,
  getCategories,
  getIngredients,
  getProductByName,
  getProducts,
  getUnits,
} from "../services/api";
import BatchCategoriesModal from "../components/BatchCategoriesModal";
import BatchIngredientsModal from "../components/BatchIngredientsModal";
import CreateSemiFinishedModal from "../components/CreateSemiFinishedModal";
import CategoryTable from "../components/CategoryTable";
import IngredientTable from "../components/IngredientTable";
import SemiFinishedTable from "../components/SemiFinishedTable";

const { Title } = Typography;

interface ApiUnit {
  id: number;
  name: string;
  abbreviation: string;
}

interface ApiCategory {
  id: number;
  name: string;
  tag?: string | null;
  units: ApiUnit[];
}

interface ApiIngredientListItem {
  id: number;
  name: string;
  category_name: string;
  unit_name: string;
  brand?: string | null;
  threshold?: number | null;
  allergen_names?: string[];
}

interface ApiSemiFinishedListItem {
  id: number;
  name: string;
  prep_time_hours: number;
  threshold?: number | null;
  unit_abbreviation?: string | null;
  ingredient_count: number;
}

interface ApiSemiFinishedIngredient {
  ingredient_id: number;
  ingredient_name: string;
  unit_abbreviation: string;
  quantity: number | string;
}

interface ApiSemiFinishedDetail {
  id: number;
  name: string;
  prep_time_hours: number;
  threshold?: number | string | null;
  unit_abbreviation?: string | null;
  ingredients: ApiSemiFinishedIngredient[];
}

interface NavItemProps {
  id: string;
  label: string;
  activeTab: string;
  onSelect: (id: string) => void;
}

const NavItem: React.FC<NavItemProps> = ({ id, label, activeTab, onSelect }) => (
  <div
    onClick={() => onSelect(id)}
    className={
      "cursor-pointer py-3 px-1 border-b-2 text-sm font-medium transition-colors " +
      (activeTab === id
        ? "border-[#1890ff] text-[#1890ff]"
        : "border-transparent text-gray-500 hover:text-[#1890ff]")
    }
  >
    {label}
  </div>
);

const getApiErrorMessage = (error: unknown, fallback: string) => {
  if (error && typeof error === "object" && "response" in error) {
    const response = (error as { response?: { data?: { detail?: string } } })
      .response;
    if (response?.data?.detail) return response.data.detail;
  }
  return fallback;
};

const BasicSettings: React.FC = () => {
  const [activeTab, setActiveTab] = useState("category");
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [semiFinishedProducts, setSemiFinishedProducts] = useState<
    SemiFinishedProduct[]
  >([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchText, setSearchText] = useState("");

  const unitsByAbbreviation = useMemo(
    () =>
      units.reduce<Record<string, string>>((acc, unit) => {
        acc[unit.abbreviation] = unit.name;
        return acc;
      }, {}),
    [units],
  );

  const fetchUnits = async () => {
    const response = await getUnits();
    const mapped = (response.data as ApiUnit[]).map((unit) => ({
      id: unit.id.toString(),
      name: unit.name,
      abbreviation: unit.abbreviation,
    }));
    setUnits(mapped);
  };

  const fetchCategories = async () => {
    const response = await getCategories();
    const mapped = (response.data as ApiCategory[]).map((category) => ({
      id: category.id.toString(),
      name: category.name,
      allowedUnits: (category.units || []).map((unit) => unit.abbreviation),
    }));
    setCategories(mapped);
  };

  const fetchIngredients = async () => {
    const response = await getIngredients();
    const mapped = (response.data as ApiIngredientListItem[]).map(
      (ingredient) => ({
      id: ingredient.id.toString(),
      name: ingredient.name,
      type: ingredient.category_name,
      brand: ingredient.brand || undefined,
      threshold_amount: ingredient.threshold ?? undefined,
      threshold_unit: ingredient.unit_name || "",
      allergens: ingredient.allergen_names || [],
    }),
    );
    setIngredients(mapped);
  };

  const fetchSemiFinishedProducts = async () => {
    const response = await getProducts();
    const list = (response.data as ApiSemiFinishedListItem[]) || [];
    const detailResponses = await Promise.all(
      list.map((product) =>
        getProductByName(product.name)
          .then((res) => res.data)
          .catch(() => null),
      ),
    );

    const mapped = detailResponses
      .filter(Boolean)
      .map((product: ApiSemiFinishedDetail) => ({
        id: product.id.toString(),
        name: product.name,
        prepTime: Number(product.prep_time_hours),
        threshold_amount: product.threshold ? Number(product.threshold) : 0,
        threshold_unit: product.unit_abbreviation || "",
        ingredients: (product.ingredients || []).map((ing) => ({
          ingredientId: ing.ingredient_id?.toString(),
          name: ing.ingredient_name,
          quantity: Number(ing.quantity),
          unit: ing.unit_abbreviation,
        })),
      }));

    setSemiFinishedProducts(mapped as SemiFinishedProduct[]);
  };

  useEffect(() => {
    const loadAll = async () => {
      try {
        await Promise.all([
          fetchUnits(),
          fetchCategories(),
          fetchIngredients(),
          fetchSemiFinishedProducts(),
        ]);
      } catch {
        message.error("Failed to load setup data.");
      }
    };

    loadAll();
  }, []);

  // Create Handlers
  const handleCategorySuccess = async (
    data: { name: string; allowedUnits: string[] }[],
  ) => {
    try {
      await Promise.all(
        data.map((item) =>
          createCategory({
            name: item.name,
            tag: null,
            unit_names: item.allowedUnits.map(
              (abbr: string) => unitsByAbbreviation[abbr] || abbr,
            ),
          }),
        ),
      );
      await fetchCategories();
      setIsModalOpen(false);
      message.success(`Successfully added ${data.length} categories.`);
    } catch (error: unknown) {
      message.error(getApiErrorMessage(error, "Failed to create categories."));
    }
  };

  const handleIngredientSuccess = async (data: Partial<Ingredient>[]) => {
    try {
      const payload = data.map((item) => ({
        name: item.name || "",
        category_name: item.type || "",
        unit_name:
          unitsByAbbreviation[item.threshold_unit || ""] ||
          item.threshold_unit ||
          "",
        brand: item.brand || null,
        threshold: item.threshold_amount ?? null,
        allergen_ids: [],
      }));
      await batchCreateIngredients(payload);
      await fetchIngredients();
      setIsModalOpen(false);
      message.success(`Successfully added ${data.length} ingredients.`);
    } catch (error: unknown) {
      message.error(getApiErrorMessage(error, "Failed to create ingredients."));
    }
  };

  const handleSemiFinishedSuccess = async (data: SemiFinishedProduct) => {
    try {
      await createProduct({
        name: data.name,
        prep_time_hours: data.prepTime,
        threshold: data.threshold_amount || null,
        unit_name:
          unitsByAbbreviation[data.threshold_unit] || data.threshold_unit || null,
        ingredients: data.ingredients.map((ingredient) => ({
          ingredient_name: ingredient.name,
          unit_name:
            unitsByAbbreviation[ingredient.unit || ""] || ingredient.unit || "",
          quantity: ingredient.quantity,
        })),
      });
      await fetchSemiFinishedProducts();
      setIsModalOpen(false);
      message.success("Successfully added semi-finished product.");
    } catch (error: unknown) {
      message.error(
        getApiErrorMessage(error, "Failed to create semi-finished product."),
      );
    }
  };

  // --- Filtered Data ---
  const filteredIngredients = ingredients.filter(
    (item) =>
      item.name.toLowerCase().includes(searchText.toLowerCase()) ||
      item.type.toLowerCase().includes(searchText.toLowerCase()) ||
      item.brand?.toLowerCase().includes(searchText.toLowerCase()),
  );

  const filteredCategories = categories.filter((item) =>
    item.name.toLowerCase().includes(searchText.toLowerCase()),
  );

  const filteredSemiFinished = semiFinishedProducts.filter((item) =>
    item.name.toLowerCase().includes(searchText.toLowerCase()),
  );

  const handleNavSelect = (id: string) => {
    setActiveTab(id);
    setSearchText("");
  };

  const renderContent = () => {
    switch (activeTab) {
      case "category":
        return <CategoryTable dataSource={filteredCategories} />;
      case "ingredients":
        return <IngredientTable dataSource={filteredIngredients} />;
      case "semifinished":
        return <SemiFinishedTable dataSource={filteredSemiFinished} />;
      case "recipe":
        return (
          <div className="p-12 text-center text-gray-400">Coming soon</div>
        );
      default:
        return (
          <div className="p-12 text-center text-gray-400">Coming soon</div>
        );
    }
  };

  return (
    <div>
      {/* Content Area */}
      <Title level={3}>Basic Settings</Title>
      <div>
        {/* Helper Navigation */}
        <div className="flex gap-1 mb-6 border-b border-gray-200">
          <NavItem
            id="category"
            label="Food Category"
            activeTab={activeTab}
            onSelect={handleNavSelect}
          />
          <NavItem
            id="ingredients"
            label="Ingredients"
            activeTab={activeTab}
            onSelect={handleNavSelect}
          />
          <NavItem
            id="semifinished"
            label="Semi-Finished Products"
            activeTab={activeTab}
            onSelect={handleNavSelect}
          />
          <NavItem
            id="recipe"
            label="Recipes"
            activeTab={activeTab}
            onSelect={handleNavSelect}
          />
          <NavItem
            id="store"
            label="Stores"
            activeTab={activeTab}
            onSelect={handleNavSelect}
          />
        </div>

        <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
          {/* Action Bar */}
          <div className="flex justify-between items-center px-4 py-4 border-b border-gray-100">
            <div className="relative w-72">
              <Input
                placeholder={`Search ${activeTab === "category" ? "categories" : activeTab === "semifinished" ? "products" : "ingredients"}...`}
                prefix={<Search size={16} className="text-gray-400" />}
                className="rounded-md"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
              />
            </div>
            {/* Only show create button for implemented tabs */}
            {(activeTab === "category" ||
              activeTab === "ingredients" ||
              activeTab === "semifinished") && (
              <Button
                type="primary"
                className="rounded-md font-medium flex items-center gap-2 px-4 shadow-sm"
                onClick={() => setIsModalOpen(true)}
              >
                <Plus size={18} />
                <span>
                  Create{" "}
                  {activeTab === "category"
                    ? "Category"
                    : activeTab === "semifinished"
                      ? "Semi-Finished Product"
                      : "Ingredient"}
                </span>
              </Button>
            )}
          </div>

          {/* Table Content */}
          {renderContent()}
        </div>
      </div>

      {activeTab === "category" && (
        <BatchCategoriesModal
          open={isModalOpen}
          onCancel={() => setIsModalOpen(false)}
          onSuccess={handleCategorySuccess}
          units={units}
        />
      )}

      {activeTab === "ingredients" && (
        <BatchIngredientsModal
          open={isModalOpen}
          onCancel={() => setIsModalOpen(false)}
          onSuccess={handleIngredientSuccess}
          categories={categories}
          units={units}
        />
      )}

      {activeTab === "semifinished" && (
        <CreateSemiFinishedModal
          open={isModalOpen}
          onCancel={() => setIsModalOpen(false)}
          onSuccess={handleSemiFinishedSuccess}
          ingredients={ingredients}
          units={units}
        />
      )}
    </div>
  );
};

export default BasicSettings;
