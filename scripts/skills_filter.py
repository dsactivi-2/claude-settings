#!/usr/bin/env python3
"""
Skills Database Filter Module
Provides advanced filtering for skills with categories, subcategories, installs, quality scores
"""

import psycopg2
import json
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class FilterOptions:
    category: Optional[str] = None
    subcategory: Optional[str] = None
    min_installs: Optional[int] = None
    max_installs: Optional[int] = None
    quality_min: Optional[int] = None
    quality_max: Optional[int] = None
    sort_by: str = "installs"
    sort_order: str = "DESC"
    limit: Optional[int] = None
    offset: int = 0

class SkillsFilter:
    """Skills database filter with advanced query capabilities"""
    
    def __init__(self, db_conn=None):
        if db_conn:
            self.conn = db_conn
        else:
            self.conn = psycopg2.connect(
                host="localhost",
                database="oi_memory",
                user="dsselmanovic"
            )
    
    def search(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Search skills with filters
        
        Args:
            category: Filter by category (exact match)
            subcategory: Filter by subcategory (exact match)
            min_installs: Minimum install count
            max_installs: Maximum install count
            quality_min: Minimum quality score (1-100)
            quality_max: Maximum quality score (1-100)
            sort_by: Sort field (installs, quality_score, name)
            sort_order: Sort direction (ASC, DESC)
            limit: Maximum results
            offset: Skip N results
        
        Returns:
            List of skill dictionaries
        """
        opts = FilterOptions(**kwargs)
        
        # Build WHERE clause
        where_clauses = []
        params = []
        param_idx = 1
        
        if opts.category:
            where_clauses.append("%s = ANY(category)")
            params.append(opts.category)

        if opts.subcategory:
            where_clauses.append("%s = ANY(subcategory)")
            params.append(opts.subcategory)

        if opts.min_installs is not None:
            where_clauses.append("installs >= %s")
            params.append(opts.min_installs)

        if opts.max_installs is not None:
            where_clauses.append("installs <= %s")
            params.append(opts.max_installs)

        if opts.quality_min is not None:
            where_clauses.append("quality_score >= %s")
            params.append(opts.quality_min)

        if opts.quality_max is not None:
            where_clauses.append("quality_score <= %s")
            params.append(opts.quality_max)
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Build ORDER BY clause
        valid_sort_fields = ["installs", "quality_score", "name", "last_updated"]
        sort_field = opts.sort_by if opts.sort_by in valid_sort_fields else "installs"
        sort_order = "DESC" if opts.sort_order.upper() == "DESC" else "ASC"
        
        # Build LIMIT/OFFSET clause
        limit_sql = ""
        if opts.limit:
            limit_sql = "LIMIT %s"
            params.append(opts.limit)

        if opts.offset > 0:
            limit_sql += " OFFSET %s"
            params.append(opts.offset)
        
        # Execute query
        query = f"""
            SELECT id, name, category, subcategory, description,
                   installs, use_cases, quality_score, last_updated
            FROM skills
            {where_sql}
            ORDER BY {sort_field} {sort_order}
            {limit_sql}
        """
        
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            columns = [desc[0] for desc in cur.description]
            results = []
            for row in cur.fetchall():
                results.append(dict(zip(columns, row)))
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT DISTINCT unnest(category) as cat FROM skills ORDER BY cat")
            return [row[0] for row in cur.fetchall()]
    
    def get_subcategories(self, category: Optional[str] = None) -> List[str]:
        """Get all unique subcategories, optionally filtered by category"""
        if category:
            query = """
                SELECT DISTINCT unnest(subcategory) as subcat
                FROM skills
                WHERE %s = ANY(category) AND subcategory IS NOT NULL
                ORDER BY subcat
            """
            with self.conn.cursor() as cur:
                cur.execute(query, (category,))
                return [row[0] for row in cur.fetchall()]
        else:
            query = """
                SELECT DISTINCT unnest(subcategory) as subcat
                FROM skills
                WHERE subcategory IS NOT NULL
                ORDER BY subcat
            """
            with self.conn.cursor() as cur:
                cur.execute(query)
                return [row[0] for row in cur.fetchall()]
    
    def stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_skills,
                    AVG(installs) as avg_installs,
                    AVG(quality_score) as avg_quality,
                    MIN(installs) as min_installs,
                    MAX(installs) as max_installs,
                    MIN(quality_score) as min_quality,
                    MAX(quality_score) as max_quality
                FROM skills
            """)
            row = cur.fetchone()
            return {
                "total_skills": row[0],
                "avg_installs": round(row[1], 2) if row[1] else 0,
                "avg_quality": round(row[2], 2) if row[2] else 0,
                "min_installs": row[3] or 0,
                "max_installs": row[4] or 0,
                "min_quality": row[5] or 0,
                "max_quality": row[6] or 0
            }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def format_table(skills: List[Dict[str, Any]]) -> str:
    """Format skills as ASCII table"""
    if not skills:
        return "No skills found."
    
    # Calculate column widths
    name_width = max(len(s['name']) for s in skills) + 2
    name_width = min(name_width, 40)  # Max 40 chars
    
    # Header
    lines = []
    lines.append(f"{'NAME':<{name_width}} {'INSTALLS':>10} {'QUALITY':>8} {'CATEGORIES':<30}")
    lines.append("-" * (name_width + 10 + 8 + 30 + 3))
    
    # Rows
    for skill in skills:
        name = skill['name'][:name_width-2] if len(skill['name']) > name_width-2 else skill['name']
        installs = f"{skill['installs']:,}" if skill['installs'] else "0"
        quality = str(skill['quality_score']) if skill['quality_score'] else "N/A"
        
        # Combine category + subcategory
        cats = []
        if skill['category']:
            cats.extend(skill['category'][:2])  # Max 2 categories
        if skill['subcategory']:
            cats.extend([f"→{s}" for s in skill['subcategory'][:2]])  # Max 2 subcategories
        cats_str = ", ".join(cats[:3])  # Max 3 total
        cats_str = cats_str[:28] if len(cats_str) > 28 else cats_str
        
        lines.append(f"{name:<{name_width}} {installs:>10} {quality:>8} {cats_str:<30}")
    
    return "\n".join(lines)

def format_json(skills: List[Dict[str, Any]]) -> str:
    """Format skills as JSON"""
    # Convert datetime to string
    for skill in skills:
        if skill.get('last_updated'):
            skill['last_updated'] = str(skill['last_updated'])
    return json.dumps(skills, indent=2, ensure_ascii=False)

def format_csv(skills: List[Dict[str, Any]]) -> str:
    """Format skills as CSV"""
    if not skills:
        return ""
    
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=skills[0].keys())
    writer.writeheader()
    for skill in skills:
        # Convert lists to strings
        row = skill.copy()
        for key, value in row.items():
            if isinstance(value, list):
                row[key] = "; ".join(str(v) for v in value)
        writer.writerow(row)
    
    return output.getvalue()

if __name__ == "__main__":
    # CLI interface
    import argparse
    
    parser = argparse.ArgumentParser(description="Filter skills database")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--subcategory", help="Filter by subcategory")
    parser.add_argument("--min-installs", type=int, help="Minimum installs")
    parser.add_argument("--max-installs", type=int, help="Maximum installs")
    parser.add_argument("--quality-min", type=int, help="Minimum quality (1-100)")
    parser.add_argument("--quality-max", type=int, help="Maximum quality (1-100)")
    parser.add_argument("--sort", default="installs", help="Sort by field (installs, quality_score, name)")
    parser.add_argument("--order", default="DESC", choices=["ASC", "DESC"], help="Sort order")
    parser.add_argument("--limit", type=int, help="Limit results")
    parser.add_argument("--offset", type=int, default=0, help="Skip N results")
    parser.add_argument("--format", default="table", choices=["table", "json", "csv"], help="Output format")
    parser.add_argument("--list-categories", action="store_true", help="List all categories")
    parser.add_argument("--list-subcategories", action="store_true", help="List all subcategories")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    
    args = parser.parse_args()
    
    try:
        filter_obj = SkillsFilter()
        
        if args.list_categories:
            cats = filter_obj.get_categories()
            print("Categories:")
            for cat in cats:
                print(f"  - {cat}")
            sys.exit(0)
        
        if args.list_subcategories:
            subcats = filter_obj.get_subcategories(args.category)
            print("Subcategories" + (f" for {args.category}" if args.category else "") + ":")
            for subcat in subcats:
                print(f"  - {subcat}")
            sys.exit(0)
        
        if args.stats:
            stats = filter_obj.stats()
            print("Skills Database Statistics:")
            print(f"  Total Skills:     {stats['total_skills']}")
            print(f"  Avg Installs:     {stats['avg_installs']:,.2f}")
            print(f"  Avg Quality:      {stats['avg_quality']:.2f}")
            print(f"  Installs Range:   {stats['min_installs']:,} - {stats['max_installs']:,}")
            print(f"  Quality Range:    {stats['min_quality']} - {stats['max_quality']}")
            sys.exit(0)
        
        # Search with filters
        results = filter_obj.search(
            category=args.category,
            subcategory=args.subcategory,
            min_installs=args.min_installs,
            max_installs=args.max_installs,
            quality_min=args.quality_min,
            quality_max=args.quality_max,
            sort_by=args.sort,
            sort_order=args.order,
            limit=args.limit,
            offset=args.offset
        )
        
        # Format output
        if args.format == "json":
            print(format_json(results))
        elif args.format == "csv":
            print(format_csv(results))
        else:
            print(format_table(results))
        
        print(f"\nFound {len(results)} skills", file=sys.stderr)
        
        filter_obj.close()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
