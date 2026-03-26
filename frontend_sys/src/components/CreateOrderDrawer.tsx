import React, { useEffect, useState } from "react";
import {
  Drawer,
  Form,
  DatePicker,
  Select,
  InputNumber,
  Input,
  Divider,
  Button,
  message,
} from "antd";
import { Trash2, PlusCircle } from "lucide-react";
import dayjs, { Dayjs } from "dayjs";
import { PurchaseOrder, Ingredient, Category, Unit } from "../types";
import {
  createPurchaseOrder,
  getCategories,
  getIngredients,
  getUnits,
} from "../services/api";

interface CreateOrderDrawerProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (newOrder: PurchaseOrder) => void;
}

interface PurchaseOrderFormItem {
  key?: number;
  name?: string;
  type?: string;
  quantity?: number;
  unit?: string;
  vendor?: string;
  price?: number;
}

interface PurchaseOrderFormValues {
  date: Dayjs;
  storeId: string;
  orderNumber?: string;
  items: PurchaseOrderFormItem[];
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

interface ApiCategory {
  id: number;
  name: string;
  units: Array<{ id: number; name: string; abbreviation: string }>;
}

interface ApiUnit {
  id: number;
  name: string;
  abbreviation: string;
}

interface ApiPurchaseOrderItem {
  id: number;
  ingredient_id: number;
  ingredient_name: string;
  unit_abbreviation: string;
  quantity: number | string;
  vendor?: string | null;
}

interface ApiPurchaseOrderDetail {
  id: number;
  po_code: string;
  order_date: string;
  store_id: string;
  total_amount: number | string;
  items: ApiPurchaseOrderItem[];
}

const CreateOrderDrawer: React.FC<CreateOrderDrawerProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const watchedItems = Form.useWatch("items", form) as PurchaseOrderFormItem[] | undefined;
  const watchedOrderNumber = Form.useWatch("orderNumber", form) as string | undefined;

  useEffect(() => {
    if (!open) return;

    const dateStr = dayjs().format("YYYYMMDD");
    const uniqueId = Math.floor(Math.random() * 10000)
      .toString()
      .padStart(4, "0");
    const newOrderNumber = `PO-${dateStr}-${uniqueId}`;
    form.setFieldsValue({
      date: dayjs(),
      storeId: "S001",
      orderNumber: newOrderNumber,
      items: [{ key: Date.now(), quantity: 1, unit: "kg" }],
    } as PurchaseOrderFormValues);

    const fetchFormData = async () => {
      try {
        const [ingredientRes, categoryRes, unitRes] = await Promise.all([
          getIngredients(),
          getCategories(),
          getUnits(),
        ]);

        const mappedIngredients = (ingredientRes.data as ApiIngredientListItem[]).map(
          (item) => ({
            id: item.id.toString(),
            name: item.name,
            type: item.category_name,
            brand: item.brand || undefined,
            threshold_amount: item.threshold ?? undefined,
            threshold_unit: item.unit_name || "",
            allergens: item.allergen_names || [],
          }),
        );

        const mappedCategories = (categoryRes.data as ApiCategory[]).map(
          (category) => ({
            id: category.id.toString(),
            name: category.name,
            allowedUnits: (category.units || []).map((unit) => unit.abbreviation),
          }),
        );

        const mappedUnits = (unitRes.data as ApiUnit[]).map((unit) => ({
          id: unit.id.toString(),
          name: unit.name,
          abbreviation: unit.abbreviation,
        }));

        setIngredients(mappedIngredients);
        setCategories(mappedCategories);
        setUnits(mappedUnits);
      } catch {
        message.error("Failed to load order form data.");
      }
    };

    fetchFormData();
  }, [open, form]);

  const handleCreateSubmit = async (values: PurchaseOrderFormValues) => {
    // Validate items
    if (!values.items || values.items.length === 0) {
      message.error("Please add at least one item.");
      return;
    }

    // Find missing ingredients
    const missingIng = values.items.some((i) => !i.name);
    if (missingIng) {
      message.error("All items must have a selected ingredient.");
      return;
    }

    try {
      const unitsByAbbrev = units.reduce<Record<string, string>>((acc, unit) => {
        acc[unit.abbreviation] = unit.name;
        return acc;
      }, {});

      const response = await createPurchaseOrder({
        order_date: values.date.format("YYYY-MM-DD"),
        store_id: values.storeId,
        items: values.items.map((item) => ({
          ingredient_name: item.name || "",
          unit_name: unitsByAbbrev[item.unit || ""] || item.unit || "",
          quantity: item.quantity || 0,
          total_amount: Number(item.price || 0),
          vendor: item.vendor || null,
        })),
      });

      const created = response.data as ApiPurchaseOrderDetail;
      const newPO: PurchaseOrder = {
        id: created.po_code,
        date: created.order_date,
        storeId: created.store_id,
        totalAmount: Number(created.total_amount || totalAmount),
        status: "Pending",
        items: (created.items || []).map((item, idx) => ({
          key: item.id?.toString() || idx.toString(),
          ingredientId: item.ingredient_id?.toString() || "",
          name: item.ingredient_name,
          quantity: Number(item.quantity),
          unit: item.unit_abbreviation,
          vendor: item.vendor || "",
        })),
      };

      onSuccess(newPO);
      form.resetFields();
      message.success("Purchase Order created successfully!");
    } catch (error: unknown) {
      if (error && typeof error === "object" && "response" in error) {
        const response = (error as { response?: { data?: { detail?: string } } })
          .response;
        message.error(response?.data?.detail || "Failed to create purchase order.");
      } else {
        message.error("Failed to create purchase order.");
      }
    }
  };

  // ... methods ...
  const handleIngredientSelect = (value: string, fieldKey: number) => {
    const ingredient = ingredients.find((i) => i.name === value);
    if (ingredient) {
      const items = (form.getFieldValue("items") || []) as PurchaseOrderFormItem[];
      const updatedItems = items.map((item, index) => {
        if (index === fieldKey) {
          const category = categories.find((c) => c.name === ingredient.type);
          const defaultUnit = category ? category.allowedUnits[0] : "kg";

          return {
            ...item,
            type: ingredient.type,
            unit: defaultUnit,
          };
        }
        return item;
      });
      form.setFieldsValue({ items: updatedItems });
    }
  };

  const getUnitOptions = (type: string) => {
    if (!type)
      return units.map((u) => ({
        value: u.abbreviation,
        label: u.abbreviation,
      }));
    const category = categories.find((c) => c.name === type);
    if (category) {
      return category.allowedUnits.map((u) => ({ value: u, label: u }));
    }
    return units.map((u) => ({
      value: u.abbreviation,
      label: u.abbreviation,
    }));
  };

  const calculateTotal = (items: PurchaseOrderFormItem[] = []) => {
    if (!items) return 0;
    return items.reduce((sum, item) => sum + (Number(item?.price) || 0), 0);
  };

  const totalAmount = calculateTotal(watchedItems || []);

  return (
    <Drawer
      title={
        <div className="flex justify-between items-center pr-8">
          <span>Create New Purchase Order</span>
        </div>
      }
      placement="bottom"
      width="100%"
      height="96%"
      onClose={onClose}
      open={open}
      styles={{ body: { padding: 0 } }}
    >
      <div className="h-full bg-white overflow-auto">
        <div className="max-w-5xl mx-auto p-8 pb-20">
          <Form
            form={form}
            layout="vertical"
            onFinish={handleCreateSubmit}
          >
            {/* Header Information */}
            <div className="grid grid-cols-3 gap-6 mb-8 bg-gray-50 p-6 rounded-lg border border-gray-100">
              <Form.Item
                name="date"
                label="Order Date"
                rules={[{ required: true }]}
                className="mb-0"
              >
                <DatePicker className="w-full" allowClear={false} />
              </Form.Item>

              <Form.Item
                name="storeId"
                label="Store ID"
                rules={[{ required: true }]}
                className="mb-0"
              >
                <div className="h-[32px] flex items-center px-3 bg-gray-100 border border-gray-300 rounded text-gray-500 font-mono cursor-default">
                  {form.getFieldValue("storeId") || "S001"}
                </div>
              </Form.Item>

              <Form.Item label="Order Number" className="mb-0">
                <div className="h-[32px] flex items-center px-3 bg-gray-100 border border-gray-300 rounded text-gray-500 font-mono select-all">
                  {watchedOrderNumber || ""}
                </div>
              </Form.Item>
            </div>

            <Divider className="!text-gray-500 !text-sm uppercase tracking-wide">
              Purchased Items
            </Divider>

            <div className="bg-gray-50/50 rounded-lg p-4 border border-gray-100">
              {/* Fixed Header Row for Table-like layout */}
              <div
                className="grid gap-4 mb-2 px-2 text-xs font-semibold text-gray-500 uppercase tracking-wide"
                style={{
                  gridTemplateColumns: "2fr 1.2fr 0.8fr 0.8fr 1.5fr 1fr 40px",
                }}
              >
                <div>
                  Ingredient <span className="text-red-500">*</span>
                </div>
                <div>Type</div>
                <div className="col-span-2">
                  Quantity / Unit <span className="text-red-500">*</span>
                </div>
                <div>Vendor</div>
                <div>
                  Total ($) <span className="text-red-500">*</span>
                </div>
                <div></div>
              </div>

              <Form.List name="items">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(({ key, name, ...restField }, index) => (
                      <div
                        key={key}
                        className="grid gap-4 items-start mb-3"
                        style={{
                          gridTemplateColumns:
                            "2fr 1.2fr 0.8fr 0.8fr 1.5fr 1fr 40px",
                        }}
                      >
                        {/* Ingredient Name */}
                        <Form.Item
                          {...restField}
                          name={[name, "name"]}
                          rules={[{ required: true, message: "Required" }]}
                          className="mb-0"
                        >
                          <Select
                            showSearch
                            placeholder="Search Ingredient"
                            optionFilterProp="label"
                            onChange={(value) =>
                              handleIngredientSelect(value, index)
                            }
                            options={ingredients.map((ing) => ({
                              value: ing.name,
                              label: ing.name,
                            }))}
                            filterOption={(input, option) =>
                              (option?.label as string)
                                .toLowerCase()
                                .includes(input.toLowerCase())
                            }
                          />
                        </Form.Item>

                        {/* Type (Auto-filled) */}
                        <Form.Item
                          noStyle
                          shouldUpdate={(prevValues, curValues) =>
                            prevValues.items?.[name]?.type !==
                            curValues.items?.[name]?.type
                          }
                        >
                          {({ getFieldValue }) => (
                            <Form.Item
                              {...restField}
                              name={[name, "type"]}
                              className="mb-0"
                            >
                              <div className="h-[32px] flex items-center px-3 bg-gray-50 border border-gray-200 rounded text-gray-500 text-sm">
                                {getFieldValue(["items", name, "type"]) || ""}
                              </div>
                            </Form.Item>
                          )}
                        </Form.Item>

                        {/* Quantity */}
                        <Form.Item
                          {...restField}
                          name={[name, "quantity"]}
                          rules={[{ required: true, message: "Required" }]}
                          className="mb-0"
                        >
                          <InputNumber
                            placeholder="0.0"
                            min={0}
                            step={0.1}
                            className="w-full"
                          />
                        </Form.Item>

                        {/* Unit (Dependent on Type) */}
                        <Form.Item
                          noStyle
                          shouldUpdate={(prevValues, curValues) =>
                            prevValues.items?.[name]?.type !==
                            curValues.items?.[name]?.type
                          }
                        >
                          {({ getFieldValue }) => {
                            const type = getFieldValue(["items", name, "type"]);
                            return (
                              <Form.Item
                                {...restField}
                                name={[name, "unit"]}
                                rules={[
                                  { required: true, message: "Required" },
                                ]}
                                className="mb-0"
                              >
                                <Select options={getUnitOptions(type)} />
                              </Form.Item>
                            );
                          }}
                        </Form.Item>

                        {/* Vendor */}
                        <Form.Item
                          {...restField}
                          name={[name, "vendor"]}
                          className="mb-0"
                        >
                          <Input placeholder="Vendor Name" />
                        </Form.Item>

                        {/* Price (Total for Line Item) */}
                        <Form.Item
                          {...restField}
                          name={[name, "price"]}
                          rules={[{ required: true, message: "Required" }]}
                          className="mb-0"
                        >
                          <InputNumber
                            placeholder="0.00"
                            min={0}
                            step={0.01}
                            prefix="$"
                            className="w-full"
                          />
                        </Form.Item>

                        {/* Remove Button */}
                        <Button
                          type="text"
                          danger
                          icon={<Trash2 size={16} />}
                          onClick={() => {
                            remove(name);
                            // Trigger math update manually if needed, or rely on onValuesChange
                            // Remove triggers onValuesChange in Antd Form
                          }}
                          className="flex items-center justify-center h-[32px]"
                        />
                      </div>
                    ))}
                    <Form.Item className="mt-4 mb-0">
                      <Button
                        type="dashed"
                        onClick={() => add()}
                        block
                        icon={<PlusCircle size={16} />}
                        className="bg-white border-blue-200 text-blue-500 hover:text-blue-600 hover:border-blue-400 hover:bg-blue-50"
                      >
                        Add Another Item
                      </Button>
                    </Form.Item>
                  </>
                )}
              </Form.List>
            </div>

            <div className="flex justify-end gap-4 mt-8 pt-4 border-t border-gray-100">
              <div className="text-right text-gray-500 text-sm flex items-center mr-4">
                <span className="text-lg font-semibold text-gray-900">
                  Total Price:{" "}
                  <span className="text-blue-600">
                    ${totalAmount.toFixed(2)}
                  </span>
                </span>
              </div>
              <Button onClick={onClose}>Cancel</Button>
              <Button
                type="primary"
                htmlType="submit"
                className="bg-blue-600 px-8 font-medium"
              >
                Submit Purchase Order
              </Button>
            </div>
          </Form>
        </div>
      </div>
    </Drawer>
  );
};

export default CreateOrderDrawer;
