import {
  Unit,
  Category,
  Ingredient,
  InventoryItem,
  PurchaseOrder,
  SemiFinishedProduct,
} from "../types";

export const mockUnits: Unit[] = [
  { id: "1", name: "Kilogram", abbreviation: "kg" },
  { id: "2", name: "Gram", abbreviation: "g" },
  { id: "3", name: "Liter", abbreviation: "L" },
  { id: "4", name: "Milliliter", abbreviation: "ml" },
  { id: "5", name: "Pieces", abbreviation: "pcs" },
  { id: "6", name: "Box", abbreviation: "box" },
  { id: "7", name: "Bottle", abbreviation: "bottle" },
  { id: "8", name: "Sheet", abbreviation: "sheets" },
  { id: "9", name: "Packet", abbreviation: "packet" },
];

export const mockCategories: Category[] = [
  { id: "1", name: "Fruit", allowedUnits: ["kg", "g", "pcs", "box"] },
  { id: "2", name: "Veggie", allowedUnits: ["kg", "g", "pcs", "box"] },
  { id: "3", name: "Meat", allowedUnits: ["kg", "g", "lb"] },
  { id: "4", name: "Grain", allowedUnits: ["kg", "g", "bags"] },
  { id: "5", name: "Dairy", allowedUnits: ["L", "ml", "g", "kg"] },
  { id: "6", name: "Fats & Oil", allowedUnits: ["L", "ml", "kg", "g"] },
  { id: "7", name: "Flavors & Spices", allowedUnits: ["g", "kg", "L", "ml"] },
  { id: "8", name: "Seafood", allowedUnits: ["kg", "g", "pcs"] },
  { id: "9", name: "Other", allowedUnits: ["pcs", "box", "kg"] },
];

export const mockIngredients: Ingredient[] = [
  {
    id: "1",
    name: "Tonkotsu Bone Broth",
    type: "Perishable",
    brand: "House Made",
    threshold_amount: 10,
    threshold_unit: "L",
    allergens: ["Wheat", "Soy"],
  },
  {
    id: "2",
    name: "Wheat Noodles (Thin)",
    type: "Fresh Goods",
    brand: "NoodleCo",
    threshold_amount: 50,
    threshold_unit: "kg",
    allergens: ["Wheat"],
  },
  {
    id: "3",
    name: "Bamboo Shoots (Menma)",
    type: "Pantry",
    brand: "Yamasa",
    threshold_amount: 5,
    threshold_unit: "kg",
  },
  {
    id: "4",
    name: "Nori Seaweed",
    type: "Dry Goods",
    brand: "Ocean Harvest",
    threshold_amount: 100,
    threshold_unit: "sheets",
    allergens: ["Fish"],
  },
  {
    id: "5",
    name: "Soft Boiled Eggs (Ajitama)",
    type: "Perishable",
    brand: "SunFarms",
    threshold_amount: 40,
    threshold_unit: "pcs",
    allergens: ["Eggs", "Soy"],
  },
];

export const mockInventory: InventoryItem[] = [
  {
    id: "i1",
    name: "Tonkotsu Bone Broth",
    ingredientId: "1", // Added missing field
    type: "Perishable",
    brand: "House Made",
    standardQty: 10,
    actualQty: 5,
    unit: "Liters",
    location: "Fridge A",
    lastUpdated: "12 mins ago",
    store_id: "102",
    status: "Restock Needed", // Added missing field
  },
  {
    id: "i2",
    name: "Wheat Noodles (Thin)",
    ingredientId: "2", // Added missing field
    type: "Fresh Goods",
    brand: "NoodleCo",
    standardQty: 100,
    actualQty: 45,
    unit: "Kg",
    location: "Shelf B",
    lastUpdated: "1 hour ago",
    store_id: "102",
    status: "Restock Needed", // Added missing field
  },
  {
    id: "i3",
    name: "Bamboo Shoots (Menma)",
    ingredientId: "3", // Added missing field
    type: "Pantry",
    brand: "Yamasa",
    standardQty: 20,
    actualQty: 1.2,
    unit: "Kg",
    location: "Storage C",
    lastUpdated: "14 mins ago",
    store_id: "102",
    status: "Restock Needed", // Added missing field
  },
  {
    id: "i4",
    name: "Nori Seaweed",
    ingredientId: "4", // Added missing field
    type: "Dry Goods",
    brand: "Ocean Harvest",
    standardQty: 1000,
    actualQty: 500,
    unit: "Sheets",
    location: "Storage D",
    lastUpdated: "4 mins ago",
    store_id: "105",
    status: "Sufficient", // Added missing field
  },
  {
    id: "i5",
    name: "Soft Boiled Eggs",
    ingredientId: "5", // Added missing field
    type: "Perishable",
    brand: "SunFarms",
    standardQty: 100,
    actualQty: 12,
    unit: "Units",
    location: "Fridge B",
    lastUpdated: "35 mins ago",
    store_id: "105",
    status: "Restock Needed", // Added missing field
  },
  // Semi-Finished Products Inventory
  {
    id: "i6",
    name: "Tonkotsu Broth Base",
    semiFinishedId: "sf1",
    type: "Semi-Finished",
    standardQty: 30,
    actualQty: 15,
    unit: "L",
    location: "Fridge A",
    lastUpdated: "30 mins ago",
    store_id: "102",
    status: "Restock Needed",
  },
  {
    id: "i7",
    name: "Marinated Soft-Boiled Egg",
    semiFinishedId: "sf2",
    type: "Semi-Finished",
    standardQty: 60,
    actualQty: 55,
    unit: "pcs",
    location: "Fridge B",
    lastUpdated: "2 hours ago",
    store_id: "102",
    status: "Sufficient",
  },
  {
    id: "i8",
    name: "Chashu Pork Roll",
    semiFinishedId: "sf3",
    type: "Semi-Finished",
    standardQty: 10,
    actualQty: 2,
    unit: "kg",
    location: "Fridge C",
    lastUpdated: "5 mins ago",
    store_id: "102",
    status: "Restock Needed",
  },
];

export const mockPurchaseOrders: PurchaseOrder[] = [
  {
    id: "PO-20260125-0004",
    storeId: "102",
    date: "2026-01-25",
    totalAmount: 450.5,
    items: [
      {
        key: "1",
        ingredientId: "1",
        name: "Pork Bones",
        quantity: 20,
        unit: "kg",
        vendor: "Local Butcher",
      },
      {
        key: "2",
        ingredientId: "2",
        name: "Wheat Noodles",
        quantity: 50,
        unit: "kg",
        vendor: "NoodleCo",
      },
    ],
    status: "Pending",
  },
  {
    id: "PO-20260124-0012",
    storeId: "105",
    date: "2026-01-24",
    totalAmount: 1200.0,
    items: [
      {
        key: "1",
        ingredientId: "4",
        name: "Nori Seaweed",
        quantity: 100,
        unit: "sheets",
        vendor: "Ocean Harvest",
      },
      {
        key: "2",
        ingredientId: "3",
        name: "Bamboo Shoots",
        quantity: 10,
        unit: "kg",
        vendor: "Yamasa",
      },
      {
        key: "3",
        ingredientId: "5",
        name: "Eggs",
        quantity: 200,
        unit: "pcs",
        vendor: "SunFarms",
      },
    ],
    status: "Completed",
  },
  {
    id: "PO-20260120-0089",
    storeId: "102",
    date: "2026-01-20",
    totalAmount: 320.0,
    items: [
      {
        key: "1",
        ingredientId: "1",
        name: "Soy Sauce",
        quantity: 20,
        unit: "L",
        vendor: "Kikkoman",
      },
    ],
    status: "Completed",
  },
];

export const mockSemiFinishedProducts: SemiFinishedProduct[] = [
  {
    id: "sf1",
    name: "Tonkotsu Broth Base",
    prepTime: 12, // hours
    threshold_amount: 20,
    threshold_unit: "L",
    ingredients: [
      { name: "Pork Bones", quantity: 10, unit: "kg" },
      { name: "Water", quantity: 50, unit: "L" },
      { name: "Yellow Onion", quantity: 2, unit: "kg" },
      { name: "Ginger", quantity: 500, unit: "g" },
      { name: "Garlic", quantity: 300, unit: "g" },
    ],
  },
  {
    id: "sf2",
    name: "Marinated Soft-Boiled Egg",
    prepTime: 4,
    threshold_amount: 50,
    threshold_unit: "pcs",
    ingredients: [
      { name: "Fresh Egg", quantity: 100, unit: "pcs", allergens: ["Eggs"] },
      {
        name: "Soy Sauce",
        quantity: 2,
        unit: "L",
        allergens: ["Soy", "Wheat"],
      },
      { name: "Mirin", quantity: 1, unit: "L" },
    ],
  },
  {
    id: "sf3",
    name: "Chashu Pork Roll",
    prepTime: 6,
    threshold_amount: 5,
    threshold_unit: "kg",
    ingredients: [
      { name: "Pork Belly", quantity: 10, unit: "kg" },
      {
        name: "Soy Sauce",
        quantity: 2,
        unit: "L",
        allergens: ["Soy", "Wheat"],
      },
      { name: "Sugar", quantity: 1, unit: "kg" },
    ],
  },
  {
    id: "sf4",
    name: "Spicy Miso Paste Mix",
    prepTime: 1.5,
    threshold_amount: 2,
    threshold_unit: "kg",
    ingredients: [
      { name: "Miso", quantity: 5, unit: "kg", allergens: ["Soy"] },
      { name: "Chili Oil", quantity: 500, unit: "ml" },
      {
        name: "Toasted Sesame",
        quantity: 200,
        unit: "g",
        allergens: ["Sesame"],
      },
    ],
  },
];

export const mockAllergens = [
  { value: "Wheat", label: "Wheat" },
  { value: "Soy", label: "Soy" },
  { value: "Eggs", label: "Eggs" },
  { value: "Milk", label: "Milk" },
  { value: "Peanuts", label: "Peanuts" },
  { value: "Tree Nuts", label: "Tree Nuts" },
  { value: "Fish", label: "Fish" },
  { value: "Shellfish", label: "Shellfish" },
  { value: "Sesame", label: "Sesame" },
];
