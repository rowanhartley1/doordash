# Import the 'math' library, which gives us access to advanced math functions like the natural logarithm (math.log).
import math

# =================================================================================================================
# --- CONFIGURATION & PERSONALIZATION (v7.8) ---
# This is the ONLY section you need to edit.
# =================================================================================================================

# 1. DEFINE YOUR WEIGHTS (Total must add up to 100)
WEIGHTS = {
    "PAY_PER_MILE": 60,        # How important is the dollar-per-mile ratio?
    "TOTAL_PAYOUT": 5,        # How important is the total cash amount?
    "END_LOCATION_FACTOR": 10, # How important is the drop-off location?
    "RESTAURANT_WAIT": 5,     # How important is avoiding slow restaurants?
    "STRATEGIC_AR_IMPACT": 20,  # How important is the strategic value of your Acceptance Rate?
}

# 2. DEFINE YOUR COSTS
COST_PER_MILE = 0.67         # The cost to run your vehicle per mile. The 2024 IRS rate is $0.67.

# 3. YOUR RESTAURANT KNOWLEDGE BASE (Using 5-Letter Codes)
RESTAURANT_KNOWLEDGE_BASE = {
    'MCDON': 4,  # McDonald's
    'WENDY': 2,  # Wendy's
    'CHILI': 3,  # Chili's
    'TACOB': 2,  # Taco Bell
    'POPEY': 2,  # Popeyes
    'CHEEF': 4,  # Cheesecake Factory
    'CHICF': 1,  #Chic-Fil-A
    'CHIPO': 1,  #Chipotle
    'DAVES': 2,  #Daves Hot Chicken
    'DEFAULT': 2.5 # This is the score used for any restaurant NOT in your list.
}


# =================================================================================================================
# --- SCORING ENGINE ---
# This is the "brain" of the algorithm. No edits needed here.
# =================================================================================================================

# --- Scoring function for Pay-Per-Mile ---
def score_pay_per_mile(payout, distance):
    if distance <= 0:
        return 0
    ppm_order = payout / distance
    ppm_average = 1.50
    score = (ppm_order / ppm_average) * 70
    return score

# --- Scoring function for Total Payout ---
def score_total_payout(payout):
    if payout < 1.01:
        return 0
    payout_benchmark_100 = 27.00
    score = (math.log(payout) / math.log(payout_benchmark_100)) * 100
    return score

# --- Scoring function for Restaurant Wait Time ---
def score_restaurant_wait(restaurant_code):
    wait_rating = RESTAURANT_KNOWLEDGE_BASE.get(
        restaurant_code.upper(), RESTAURANT_KNOWLEDGE_BASE['DEFAULT']
    )
    if wait_rating == 1: return 100
    if wait_rating == 2: return 80
    if wait_rating == 3: return 40
    if wait_rating == 4: return 20
    if wait_rating == 2.5: return 60
    return 80

# --- Scoring function for Strategic AR Impact ---
def score_strategic_ar_impact(current_ar):
    if 50 <= current_ar < 60:
        return 150 - 15 * (current_ar - 50)
    elif 70 <= current_ar < 80:
        return 75 - 7.5 * (current_ar - 70)
    elif current_ar >= 60:
        return 10
    else:
        return 150

# --- Scoring function for the End Location ---
def score_end_location_compass(distance_category):
    if distance_category == 's': return 100
    if distance_category == 'sm': return 80
    if distance_category == 'm': return 60
    if distance_category == 'ml': return 40
    if distance_category == 'l': return 20
    return 60


# --- The Main Evaluator ---
def evaluate_order(order_data):
    scores = {
        "PAY_PER_MILE": score_pay_per_mile(order_data['payout'], order_data['distance']),
        "TOTAL_PAYOUT": score_total_payout(order_data['payout']),
        "RESTAURANT_WAIT": score_restaurant_wait(order_data['restaurant_code']),
        "STRATEGIC_AR_IMPACT": score_strategic_ar_impact(order_data['current_ar']),
        "END_LOCATION_FACTOR": score_end_location_compass(order_data['dist_category']),
    }
    
    # Calculate the raw, uncapped score by applying the weights.
    total_weighted_score = sum(scores[key] * (weight / 100.0) for key, weight in WEIGHTS.items())
    # We keep this raw score as a whole number. This is the number that could be 28000.
    uncapped_score = int(total_weighted_score)

    # ########################################################################
    # ### NEW (v7.8): This block determines the final display string      ###
    # ### It looks at the uncapped score BEFORE capping it.               ###
    # ########################################################################
    score_display_string = ""
    if uncapped_score >= 150:
        # If the true score is 150+, it's an epic order.
        score_display_string = "100++"
    elif uncapped_score >= 125:
        # If the true score is 125-149, it's a unicorn order.
        score_display_string = "100+"
    else:
        # For any other score (including 101, 110, etc.), cap it at 100.
        final_capped_score = min(100, uncapped_score)
        score_display_string = str(final_capped_score)

    # --- This section prints the final report to your screen ---
    print("\n" + "="*35)
    print("      EVALUATION REPORT")
    print("="*35)
    
    payout = order_data['payout']
    ppm = (payout / order_data['distance']) if order_data['distance'] > 0 else 0
    
    report_lines = {
        "TOTAL_PAYOUT": f"(${payout:<4.2f})",
        "PAY_PER_MILE": f"(${ppm:<4.2f}/mi)",
        "STRATEGIC_AR_IMPACT": f"(@ {order_data['current_ar']}%)",
        "RESTAURANT_WAIT": "",
        "END_LOCATION_FACTOR": ""
    }
    
    for key, weight in WEIGHTS.items():
        print(f"- {key:<21} | Score: {int(scores[key]):>3} | {report_lines[key]:<10}")
        
    print("-"*35)
    # This now prints the new display string, which will be "100", "100+", or "100++"
    print(f"  FINAL SCORE: {score_display_string}")
    print("="*35 + "\n")
    return score_display_string


# =================================================================================================================
# --- INTERACTIVE PROMPT INTERFACE ---
# =================================================================================================================

def get_validated_input(prompt, type_converter):
    while True:
        try:
            return type_converter(input(prompt))
        except (ValueError, TypeError):
            print("  ! Invalid input. Please try again.")

def run_interactive_session():
    print("--- DoorDash Compass Tool v7.8 ---")
    print("Enter order details sequentially.")

    payout = get_validated_input("Payout ($): ", float)
    distance = get_validated_input("Distance (miles): ", float)
    restaurant_code = input("Restaurant (first 5 letters): ").strip()[:5]

    while True:
        dist_category = input("Drop-off distance from Hotspot? (s=short, sm=short-medium, m=medium, ml=medium-long, l=long): ").lower()
        if dist_category in ['s', 'sm', 'm', 'ml', 'l']:
            break
        print("  ! Invalid. Please enter s, sm, m, ml, or l.")
    
    current_ar = get_validated_input("Your Current AR (%): ", int)

    order_data = {
        'payout': payout,
        'distance': distance,
        'restaurant_code': restaurant_code,
        'dist_category': dist_category,
        'current_ar': current_ar,
    }
    
    evaluate_order(order_data)

# --- SCRIPT EXECUTION ---
if __name__ == '__main__':
    while True:
        run_interactive_session()
        again = input("Evaluate another order? (y/n): ").lower()
        if again != 'y':
            print("\nHappy Dashing!")
            break
        print("\n" + "="*40 + "\n")