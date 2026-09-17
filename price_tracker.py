#!/usr/bin/env python3


import sys
import json
import os
import time
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate
from trackers import get_tracker

init(autoreset=True)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'tracked_items.json')




def load_items():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_items(items):
    with open(DATA_FILE, 'w') as f:
        json.dump(items, f, indent=2)




def add_item(url, target_price=None):
    items = load_items()
    
    print(f"{Fore.CYAN}Fetching product info...")
    try:
        tracker = get_tracker(url)
        title = tracker.get_title(url)
        current_price = tracker.get_price(url)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        return
    
    item = {
        'url': url,
        'title': title[:80],
        'target_price': float(target_price) if target_price else None,
        'initial_price': current_price,
        'current_price': current_price,
        'last_checked': datetime.now().isoformat(),
    }
    
    # Check for duplicate
    for existing in items:
        if existing['url'] == url:
            print(f"{Fore.YELLOW}Item already tracked!")
            return
    
    items.append(item)
    save_items(items)
    
    print(f"{Fore.GREEN}✓ Added: {title}")
    print(f"{Fore.GREEN}  Current price: ${current_price:.2f}")
    if target_price:
        print(f"{Fore.GREEN}  Target price: ${float(target_price):.2f}")


def remove_item(index):
    items = load_items()
    try:
        idx = int(index) - 1
        if 0 <= idx < len(items):
            removed = items.pop(idx)
            save_items(items)
            print(f"{Fore.GREEN}✓ Removed: {removed['title']}")
        else:
            print(f"{Fore.RED}Invalid index")
    except ValueError:
        print(f"{Fore.RED}Index must be a number")


def list_items():
    items = load_items()
    if not items:
        print(f"{Fore.YELLOW}No items tracked yet. Use 'add <url>' to add.")
        return
    
    table_data = []
    for i, item in enumerate(items, 1):
        target = f"${item['target_price']:.2f}" if item.get('target_price') else "—"
        current = f"${item['current_price']:.2f}" if item.get('current_price') else "—"
        diff = item['current_price'] - item['initial_price'] if item.get('current_price') else 0
        
        if diff < 0:
            diff_str = f"{Fore.GREEN}${diff:.2f}"
        elif diff > 0:
            diff_str = f"{Fore.RED}+${diff:.2f}"
        else:
            diff_str = f"{Fore.WHITE}$0.00"
        
        table_data.append([
            i, item['title'][:50], current, target, diff_str
        ])
    
    print(tabulate(table_data, 
                   headers=['#', 'Product', 'Current', 'Target', 'Change'],
                   tablefmt='grid'))


def check_prices():
    items = load_items()
    if not items:
        print(f"{Fore.YELLOW}No items to check.")
        return
    
    print(f"{Fore.CYAN}Checking prices...\n")
    
    for i, item in enumerate(items, 1):
        try:
            tracker = get_tracker(item['url'])
            new_price = tracker.get_price(item['url'])
            old_price = item['current_price']
            
            item['current_price'] = new_price
            item['last_checked'] = datetime.now().isoformat()
            
            change = new_price - old_price
            if abs(change) < 0.01:
                status = f"{Fore.WHITE}No change"
            elif change < 0:
                status = f"{Fore.GREEN}▼ ${abs(change):.2f} (${new_price:.2f})"
            else:
                status = f"{Fore.RED}▲ ${change:.2f} (${new_price:.2f})"
            
            print(f"{i}. {item['title'][:60]}")
            print(f"   {status}")
            
            # Check target price
            if item.get('target_price') and new_price <= item['target_price']:
                print(f"   {Fore.GREEN}{Style.BRIGHT}🎯 TARGET REACHED! "
                      f"Target: ${item['target_price']:.2f}, Now: ${new_price:.2f}")
            
            print()
        except Exception as e:
            print(f"{i}. {item['title'][:60]}")
            print(f"   {Fore.RED}Error: {e}\n")
    
    save_items(items)


def watch_prices(interval_minutes=30):
    """Continuously check prices at intervals"""
    print(f"{Fore.CYAN}Watching prices every {interval_minutes} minutes. "
          f"Press Ctrl+C to stop.\n")
    try:
        while True:
            print(f"{Fore.CYAN}[{datetime.now().strftime('%H:%M:%S')}] Checking...")
            check_prices()
            print(f"{Fore.CYAN}Next check in {interval_minutes} minutes.\n")
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopped watching.")


# ---------- CLI ----------

def print_usage():
    print(f"""{Fore.CYAN}
Terminal Price Tracker
======================
Usage:
  python price_tracker.py add <url> [target_price]   Add product to track
  python price_tracker.py remove <index>              Remove product
  python price_tracker.py list                        List tracked products
  python price_tracker.py check                       Check prices once
  python price_tracker.py watch [interval_minutes]    Check periodically
""")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'add':
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: URL required")
            return
        url = sys.argv[2]
        target = sys.argv[3] if len(sys.argv) > 3 else None
        add_item(url, target)
    
    elif command == 'remove':
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: index required")
            return
        remove_item(sys.argv[2])
    
    elif command == 'list':
        list_items()
    
    elif command == 'check':
        check_prices()
    
    elif command == 'watch':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        watch_prices(interval)
    
    else:
        print(f"{Fore.RED}Unknown command: {command}")
        print_usage()


if __name__ == '__main__':
    main()
