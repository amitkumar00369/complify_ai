class PaginationRsponse:
    @staticmethod
    def returnData(data,query):
        try:
            print(query)
            limit = query['limit']
            page = query['page']
            total_docs = len(data)
            total_pages = (total_docs + limit - 1) // limit
            offset = (page - 1) * limit
            paged_queryset = data[offset : offset + limit]
            # Build response
            return  {
                    "docs": paged_queryset,
                    "totalDocs": total_docs,
                    "limit": limit,
                    "page": page,
                    "totalPages": total_pages,
                    "pagingCounter": offset + 1,
                    "hasPrevPage": page > 1,
                    "hasNextPage": page < total_pages,
                    "prevPage": page - 1 if page > 1 else None,
                    "nextPage": page + 1 if page < total_pages else None,
                },
        except Exception as e:
            print(str(e))
        
        