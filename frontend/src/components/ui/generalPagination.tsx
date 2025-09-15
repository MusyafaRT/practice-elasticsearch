import React from "react";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationEllipsis,
  PaginationPrevious,
  PaginationNext,
} from "@/components/ui/pagination"; // adjust path as needed

interface GeneralPaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  maxVisiblePages?: number; // optional, default 5
}

const GeneralPagination: React.FC<GeneralPaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  maxVisiblePages = 5,
}) => {
  if (totalPages <= 1) return null;

  const createPageNumbers = () => {
    const pages: (number | "ellipsis")[] = [];

    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);

      const left = Math.max(2, currentPage - 1);
      const right = Math.min(totalPages - 1, currentPage + 1);

      if (left > 2) pages.push("ellipsis");

      for (let i = left; i <= right; i++) pages.push(i);

      if (right < totalPages - 1) pages.push("ellipsis");

      pages.push(totalPages);
    }

    return pages;
  };

  const pageNumbers = createPageNumbers();

  return (
    <Pagination>
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious
            href="#"
            className=""
            onClick={(e) => {
              e.preventDefault();
              if (currentPage > 1) onPageChange(currentPage - 1);
            }}
          />
        </PaginationItem>

        {pageNumbers.map((page, idx) =>
          page === "ellipsis" ? (
            <PaginationItem key={idx}>
              <PaginationEllipsis />
            </PaginationItem>
          ) : (
            <PaginationItem key={idx}>
              <PaginationLink
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  onPageChange(page as number);
                }}
                aria-current={page === currentPage ? "page" : undefined}
                className={`${page === currentPage ? "font-bold bg-blue-950 text-white" : ""}`}
              >
                {page}
              </PaginationLink>
            </PaginationItem>
          )
        )}

        <PaginationItem>
          <PaginationNext
            href="#"
            onClick={(e) => {
              e.preventDefault();
              if (currentPage < totalPages) onPageChange(currentPage + 1);
            }}
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
};

export default GeneralPagination;
