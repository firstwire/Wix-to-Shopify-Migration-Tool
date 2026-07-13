"""
Wix to Shopify Migration Tool
=============================
Single script handling Products, Orders, and Customers CSV migration
from Wix exports to Shopify-import-ready CSV files.

USAGE:
    python migrate.py --type products
    python migrate.py --type orders
    python migrate.py --type customers
    python migrate.py --type all
    python migrate.py                     (interactive menu if no --type given)

Optional custom paths:
    python migrate.py --type products --input input/my_products.csv --output output/my_result.csv
"""

import argparse
import re
from pathlib import Path

import pandas as pd

# ============================================================
# SHARED HELPERS
# ============================================================

WIX_MEDIA_BASE_URL = "https://static.wixstatic.com/media/"

COUNTRY_CODES = {
    "india": "IN", "united states": "US", "usa": "US",
    "united kingdom": "GB", "uk": "GB", "canada": "CA", "australia": "AU",
}

INDIA_STATE_CODES = {
    "andhra pradesh": "AP", "arunachal pradesh": "AR", "assam": "AS",
    "bihar": "BR", "chhattisgarh": "CT", "goa": "GA", "gujarat": "GJ",
    "haryana": "HR", "himachal pradesh": "HP", "jharkhand": "JH",
    "karnataka": "KA", "kerala": "KL", "madhya pradesh": "MP",
    "maharashtra": "MH", "manipur": "MN", "meghalaya": "ML",
    "mizoram": "MZ", "nagaland": "NL", "odisha": "OR", "punjab": "PB",
    "rajasthan": "RJ", "sikkim": "SK", "tamil nadu": "TN",
    "telangana": "TG", "tripura": "TR", "uttar pradesh": "UP",
    "uttarakhand": "UT", "west bengal": "WB", "delhi": "DL",
    "jammu and kashmir": "JK", "ladakh": "LA", "puducherry": "PY",
    "chandigarh": "CH",
}


def clean_value(value):
    """Strip whitespace and stray literal quote characters Wix sometimes
    embeds inside values (e.g. phone numbers, zip codes)."""
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.startswith('"') and value.endswith('"') and len(value) > 1:
        value = value[1:-1].strip()
    return value


def sanitize_handle(text):
    """Convert text into a Shopify-safe handle (lowercase, hyphenated)."""
    if pd.isna(text) or str(text).strip() == "":
        return ""
    text = str(text).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def build_image_url(filename):
    """Wix CSV exports only give the bare filename (e.g. 'abc123~mv2.png'),
    not a full URL. Shopify requires a real https:// URL, so reconstruct
    it using Wix's documented static media CDN pattern."""
    filename = str(filename).strip()
    if not filename or filename.lower() == "nan":
        return ""
    if filename.startswith(("http://", "https://")):
        return filename
    return WIX_MEDIA_BASE_URL + filename


def validate_image_url(url):
    if pd.isna(url) or str(url).strip() == "":
        return True
    return str(url).startswith(("http://", "https://"))


def get_country_code(country_name):
    return COUNTRY_CODES.get(clean_value(country_name).lower(), "")


def get_province_code(state_name, country_name):
    if clean_value(country_name).lower() == "india":
        return INDIA_STATE_CODES.get(clean_value(state_name).lower(), "")
    return ""


def marketing_to_yesno(value):
    return "yes" if clean_value(value).lower() == "subscribed" else "no"


def load_csv(input_path):
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"ERROR: File not found at {input_path.resolve()}")
        return None
    df = pd.read_csv(input_path, encoding="utf-8-sig", dtype=str)
    df = df.fillna("")
    if df.empty:
        print("ERROR: Input CSV has no rows.")
        return None
    return df


# ============================================================
# PRODUCTS
# ============================================================

def convert_products(input_path, output_path):
    df = load_csv(input_path)
    if df is None:
        return None

    required_cols = ["handleId", "name"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"ERROR: Missing required Wix columns: {missing}")
        return None

    shopify_rows = []
    invalid_image_count = 0
    grouped = df.groupby("handleId", sort=False)

    for handle_id, group in grouped:
        handle = sanitize_handle(handle_id)
        first_row = group.iloc[0]

        image_urls = []
        if "productImageUrl" in group.columns:
            for raw in group["productImageUrl"].tolist():
                full_url = build_image_url(raw)
                if not full_url:
                    continue
                if not validate_image_url(full_url):
                    invalid_image_count += 1
                    continue
                if full_url not in image_urls:
                    image_urls.append(full_url)

        for i, (_, row) in enumerate(group.iterrows()):
            is_first = (i == 0)
            shopify_rows.append({
                "Handle": handle,
                "Title": first_row.get("name", "") if is_first else "",
                "Body (HTML)": first_row.get("description", "") if is_first else "",
                "Vendor": first_row.get("brand", "") if is_first else "",
                "Product Category": "",
                "Type": "",
                "Tags": first_row.get("collection", "") if is_first else "",
                "Published": "TRUE" if first_row.get("visible", "true").lower() != "false" else "FALSE",
                "Option1 Name": row.get("productOptionName1", ""),
                "Option1 Value": row.get("productOptionDescription1", ""),
                "Option2 Name": row.get("productOptionName2", ""),
                "Option2 Value": row.get("productOptionDescription2", ""),
                "Variant SKU": row.get("sku", ""),
                "Variant Inventory Qty": row.get("inventory", "0"),
                "Variant Price": row.get("price", ""),
                "Variant Compare At Price": row.get("surcharge", ""),
                "Variant Grams": row.get("weight", ""),
                "Image Src": "",
                "Image Position": "",
                "SEO Title": first_row.get("name", "") if is_first else "",
                "SEO Description": first_row.get("description", "") if is_first else "",
                "Status": "active",
            })

        if image_urls:
            shopify_rows[len(shopify_rows) - len(group)]["Image Src"] = image_urls[0]
            shopify_rows[len(shopify_rows) - len(group)]["Image Position"] = "1"
            for pos, url in enumerate(image_urls[1:], start=2):
                shopify_rows.append({
                    "Handle": handle, "Title": "", "Body (HTML)": "", "Vendor": "",
                    "Product Category": "", "Type": "", "Tags": "", "Published": "",
                    "Option1 Name": "", "Option1 Value": "", "Option2 Name": "",
                    "Option2 Value": "", "Variant SKU": "", "Variant Inventory Qty": "",
                    "Variant Price": "", "Variant Compare At Price": "", "Variant Grams": "",
                    "Image Src": url, "Image Position": str(pos),
                    "SEO Title": "", "SEO Description": "", "Status": "",
                })

    out_df = pd.DataFrame(shopify_rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)

    print("=" * 60)
    print("PRODUCTS CONVERSION COMPLETE")
    print("=" * 60)
    print(f"Input rows read: {len(df)}")
    print(f"Output rows written: {len(out_df)}")
    print(f"Unique products (handles): {df['handleId'].nunique()}")
    if invalid_image_count:
        print(f"WARNING: {invalid_image_count} image URL(s) skipped as invalid.")
    print(f"Output file saved to: {output_path.resolve()}")
    return out_df


# ============================================================
# ORDERS
# ============================================================

def convert_orders(input_path, output_path):
    df = load_csv(input_path)
    if df is None:
        return None

    required_cols = ["Order number", "Contact email"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"ERROR: Missing required Wix columns: {missing}")
        return None

    output_rows = []
    for _, row in df.iterrows():
        output_rows.append({
            "Name": clean_value(row.get("Order number", "")),
            "Email": clean_value(row.get("Contact email", "")),
            "Financial Status": clean_value(row.get("Payment status", "")),
            "Fulfillment Status": clean_value(row.get("Fulfillment status", "")),
            "Currency": clean_value(row.get("Currency", "")),
            "Lineitem name": clean_value(row.get("Item", "")),
            "Lineitem variant": clean_value(row.get("Variant", "")),
            "Lineitem sku": clean_value(row.get("SKU", "")),
            "Lineitem quantity": clean_value(row.get("Qty", "")),
            "Lineitem price": clean_value(row.get("Price", "")),
            "Shipping Method": clean_value(row.get("Delivery method", "")),
            "Shipping Name": clean_value(row.get("Recipient name", "")),
            "Shipping Phone": clean_value(row.get("Recipient phone", "")),
            "Shipping Address1": clean_value(row.get("Delivery address", "")),
            "Shipping City": clean_value(row.get("Delivery city", "")),
            "Shipping Province": clean_value(row.get("Delivery state", "")),
            "Shipping Zip": clean_value(row.get("Delivery zip/postal code", "")),
            "Shipping Country": clean_value(row.get("Delivery country", "")),
            "Billing Name": clean_value(row.get("Billing name", "")),
            "Billing Address1": clean_value(row.get("Billing address", "")),
            "Billing City": clean_value(row.get("Billing city", "")),
            "Billing Province": clean_value(row.get("Billing state", "")),
            "Billing Zip": clean_value(row.get("Billing zip/postal code", "")),
            "Billing Country": clean_value(row.get("Billing country", "")),
            "Total": clean_value(row.get("Total", "")),
            "Taxes": clean_value(row.get("Total tax", "")),
            "Shipping": clean_value(row.get("Shipping rate", "")),
            "Note": clean_value(row.get("Note from customer", "")),
        })

    out_df = pd.DataFrame(output_rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)

    print("=" * 60)
    print("ORDERS CONVERSION COMPLETE")
    print("=" * 60)
    print(f"Input rows read: {len(df)}")
    print(f"Output rows written: {len(out_df)}")
    print(f"Unique orders: {df['Order number'].nunique()}")
    print(f"Output file saved to: {output_path.resolve()}")
    print("\nNOTE: Shopify has no native CSV order import in admin.")
    print("Use this output with an order-import app (e.g. Order's Up, EZ Importer).")
    return out_df


# ============================================================
# CUSTOMERS
# ============================================================

def convert_customers(input_path, output_path):
    df = load_csv(input_path)
    if df is None:
        return None

    if "Email" not in df.columns:
        print("ERROR: Missing required 'Email' column.")
        return None

    dup_emails = df["Email"][df["Email"].str.strip() != ""]
    dup_emails = dup_emails[dup_emails.duplicated(keep=False)]
    if not dup_emails.empty:
        print(f"WARNING: {dup_emails.nunique()} duplicate email(s) found - "
              f"Shopify keeps only the last row per duplicate on import:")
        for email in dup_emails.unique():
            print(f"  - {email}")

    output_rows = []
    missing_email_count = 0

    for _, row in df.iterrows():
        email = clean_value(row.get("Email", ""))
        if not email:
            missing_email_count += 1

        country = clean_value(row.get("Country", ""))
        state = clean_value(row.get("State", ""))

        note_parts = []
        existing_note = clean_value(row.get("Notes", ""))
        if existing_note:
            note_parts.append(existing_note)
        for label, col in [
            ("Wix joined date", "Joined Date"),
            ("Wix last order date", "Last Order Date"),
            ("Wix total orders", "Total Orders"),
            ("Wix total spent", "Total Spent"),
        ]:
            val = clean_value(row.get(col, ""))
            if val:
                note_parts.append(f"{label}: {val}")

        tags = [t.strip() for t in clean_value(row.get("Tags", "")).split(",") if t.strip()]
        status = clean_value(row.get("Status", ""))
        if status:
            tags.append(status)

        phone = clean_value(row.get("Phone", ""))

        output_rows.append({
            "First Name": clean_value(row.get("First Name", "")),
            "Last Name": clean_value(row.get("Last Name", "")),
            "Email": email,
            "Accepts Email Marketing": marketing_to_yesno(row.get("Marketing Consent", "")),
            "Default Address Company": clean_value(row.get("Company", "")),
            "Default Address Address1": clean_value(row.get("Address 1", "")),
            "Default Address Address2": clean_value(row.get("Address 2", "")),
            "Default Address City": clean_value(row.get("City", "")),
            "Default Address Province Code": get_province_code(state, country),
            "Default Address Country Code": get_country_code(country),
            "Default Address Zip": clean_value(row.get("Zip Code", "")),
            "Default Address Phone": phone,
            "Phone": phone,
            "Accepts SMS Marketing": "no",
            "Tags": ", ".join(tags),
            "Note": " | ".join(note_parts),
            "Tax Exempt": "no",
        })

    out_df = pd.DataFrame(output_rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)

    print("=" * 60)
    print("CUSTOMERS CONVERSION COMPLETE")
    print("=" * 60)
    print(f"Input rows read: {len(df)}")
    print(f"Output rows written: {len(out_df)}")
    if missing_email_count:
        print(f"NOTE: {missing_email_count} row(s) have no email.")
    print(f"Output file saved to: {output_path.resolve()}")
    return out_df


# ============================================================
# CLI ENTRY POINT
# ============================================================

DEFAULTS = {
    "products": ("input/wix_products.csv", "output/shopify_products.csv", convert_products),
    "orders": ("input/wix_orders.csv", "output/shopify_orders.csv", convert_orders),
    "customers": ("input/wix_customers.csv", "output/shopify_customers.csv", convert_customers),
}


def run_migration(migration_type, input_path=None, output_path=None):
    default_in, default_out, func = DEFAULTS[migration_type]
    func(input_path or default_in, output_path or default_out)


def interactive_menu():
    print("Wix to Shopify Migration Tool")
    print("1. Products")
    print("2. Orders")
    print("3. Customers")
    print("4. All three")
    choice = input("Select an option (1-4): ").strip()
    mapping = {"1": ["products"], "2": ["orders"], "3": ["customers"],
               "4": ["products", "orders", "customers"]}
    selected = mapping.get(choice)
    if not selected:
        print("Invalid choice.")
        return
    for m in selected:
        run_migration(m)
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wix to Shopify CSV Migration Tool")
    parser.add_argument("--type", choices=["products", "orders", "customers", "all"],
                         help="Which migration to run")
    parser.add_argument("--input", help="Custom input CSV path (single-type only)")
    parser.add_argument("--output", help="Custom output CSV path (single-type only)")
    args = parser.parse_args()

    if not args.type:
        interactive_menu()
    elif args.type == "all":
        for m in ["products", "orders", "customers"]:
            run_migration(m)
            print()
    else:
        run_migration(args.type, args.input, args.output)