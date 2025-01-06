"use client";

import { Range } from "react-date-range";
import Button from "../Button";
import Calendar from "../inputs/Calendar";
import { SafeUser } from "@/app/types";

interface ListingReservationProps {
  price: number;
  dateRange: Range;
  totalPrice: number;
  onChangeDate: (value: Range) => void;
  onSubmitMain: () => void;
  onSubmitSecondary: () => void;
  disabled?: boolean;
  disabledDates: Date[];
  currentUser: SafeUser | null;
}

const ListingReservation: React.FC<ListingReservationProps> = ({
  price,
  dateRange,
  totalPrice,
  onChangeDate,
  onSubmitMain,
  onSubmitSecondary,
  disabled,
  disabledDates,
  currentUser,
}) => {
  return (
    <div className="bg-white rounded-xl border-[1px] border-neutral-200 overflow-hidden">
      <div className="flex flex-row items-center gap-1 p-4">
        <div className="text-2xl font-semibold">$ {price}</div>
        <div className="font-light text-neutral-600 ">night</div>
      </div>
      <hr />
      <Calendar
        value={dateRange}
        disabledDates={disabledDates}
        onChange={(value) => onChangeDate(value.selection)}
      />
      <hr />
      {currentUser && (
        <>
          <div className="p-4">
            <Button
              disabled={disabled}
              label="Pay and Reserve"
              onClick={onSubmitMain}
            />
          </div>
          <div className="px-4">
            <Button
              outline={true}
              disabled={disabled}
              label="Reserve"
              onClick={onSubmitSecondary}
            />
          </div>
        </>
      )}
      <div className="p-4 flex flex-row items-center justify-between font-semibold text-lg">
        <div>Total</div>
        <div>$ {totalPrice}</div>
      </div>
    </div>
  );
};

export default ListingReservation;
