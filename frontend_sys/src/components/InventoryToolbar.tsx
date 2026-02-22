import React from "react";
import { Input, Select } from "antd";
import { Search } from "lucide-react";

interface Option {
  value: string;
  label: string;
}

interface InventoryToolbarProps {
  searchText: string;
  onSearchChange: (value: string) => void;
  // Filters
  filterLabel?: string;
  locationFilter: string[];
  onLocationFilterChange: (value: string[]) => void;
  locationOptions: Option[];
  typeFilter: string[];
  onTypeFilterChange: (value: string[]) => void;
  typeOptions: Option[];
  locationPlaceholder?: string;
  // View Options
  groupBy: string;
  onGroupByChange: (value: string) => void;
  groupByOptions: Option[];
  sortBy: string;
  onSortByChange: (value: string) => void;
  sortByOptions: Option[];
}

const InventoryToolbar: React.FC<InventoryToolbarProps> = ({
  searchText,
  onSearchChange,
  filterLabel = "Filter",
  locationFilter,
  onLocationFilterChange,
  locationOptions,
  typeFilter,
  onTypeFilterChange,
  typeOptions,
  locationPlaceholder = "Location",
  groupBy,
  onGroupByChange,
  groupByOptions,
  sortBy,
  onSortByChange,
  sortByOptions,
}) => {
  return (
    <div className="flex flex-col space-y-4 mb-6 bg-gray-50 p-4 rounded-lg border border-gray-100">
      {/* Search Row */}
      <div className="w-full">
        <Input
          prefix={<Search size={16} className="text-gray-400" />}
          placeholder="Search item name, brand..." // Generic placeholder
          className="w-full"
          size="middle"
          value={searchText}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      {/* Controls Row */}
      <div className="flex flex-col md:flex-row justify-between gap-4 items-center">
        {/* Left: Filters */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <span className="text-gray-500 text-xs font-semibold uppercase tracking-wide">
            {filterLabel}
          </span>
          <Select
            mode="multiple"
            placeholder={locationPlaceholder}
            allowClear
            className="w-36"
            maxTagCount="responsive"
            size="small"
            value={locationFilter}
            onChange={onLocationFilterChange}
            options={locationOptions}
          />
          <Select
            mode="multiple"
            placeholder="Type"
            allowClear
            className="w-36"
            maxTagCount="responsive"
            size="small"
            value={typeFilter}
            onChange={onTypeFilterChange}
            options={typeOptions}
          />
        </div>

        {/* Right: View Options */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end">
          <span className="text-gray-500 text-xs font-semibold uppercase tracking-wide">
            View
          </span>
          <Select
            value={groupBy}
            onChange={onGroupByChange}
            className="w-36"
            size="small"
            options={groupByOptions}
          />
          <Select
            value={sortBy}
            onChange={onSortByChange}
            className="w-36"
            size="small"
            options={sortByOptions}
          />
        </div>
      </div>
    </div>
  );
};

export default InventoryToolbar;
