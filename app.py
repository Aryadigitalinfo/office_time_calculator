# app.py
import streamlit as st
from calculator import calculate_office_time
import pytz

def main():
    st.set_page_config(
        page_title="Office Time Calculator", 
        page_icon="⏰",
        layout="wide"
    )
    
    st.title("⏰ Office Time Calculator")
    st.markdown("Paste your biometric log data below to calculate work and break times.")
    
    # Timezone selection
    timezones = [
        'UTC', 'Asia/Kolkata', 'Asia/Dubai', 'Europe/London', 
        'US/Eastern', 'US/Central', 'US/Pacific', 'Europe/Paris',
        'Asia/Singapore', 'Australia/Sydney', 'Asia/Tokyo'
    ]
    
    selected_timezone = st.selectbox(
        "Select your timezone",
        timezones,
        index=1,  # Default to Asia/Kolkata
        help="Choose the timezone for your location"
    )
    
    # Display current time in selected timezone
    try:
        tz = pytz.timezone(selected_timezone)
        current_time = st.empty()
        current_time.info(f"Current time in {selected_timezone}: {datetime.now(tz).strftime('%Y-%m-%d %H:%M %Z')}")
    except:
        st.warning("Could not display current time information")
    
    # Input area
    raw_text = st.text_area(
        "Biometric Log Input",
        placeholder="Paste your biometric log here (with 'Biometric.' lines)...\nExample:\nBiometric. 09:00\nBiometric. 13:00\nBiometric. 14:00\nBiometric. 18:00",
        height=200
    )
    
    if st.button("Calculate Times", type="primary"):
        if not raw_text.strip():
            st.error("Please paste your biometric log data.")
            return
        
        try:
            result = calculate_office_time(raw_text, selected_timezone)
            
            # st.success(f"Calculation completed! (Using {selected_timezone} timezone)")
            
            # Display current time used for calculation
            # st.info(f"Calculation based on current time: {result.get('current_time', 'N/A')}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Work Time", 
                    f"{result['work_hours']}h {result['work_minutes']}m",
                    help="Target: 7h 30m"
                )
            
            with col2:
                st.metric(
                    "Total Break Time", 
                    f"{result['break_hours']}h {result['break_minutes']}m",
                    help="Target: 1h 30m"
                )
            
            rw_h, rw_m = result["remaining_work"]
            rb_h, rb_m = result["remaining_break"]
            
            with col3:
                st.metric(
                    "Remaining Work", 
                    f"{rw_h}h {rw_m}m",
                    # delta=f"{'-' if rw_h > 0 or rw_m > 0 else ''}{rw_h}h {rw_m}m",
                    # delta_color="inverse"
                )
            
            with col4:
                st.metric(
                    "Remaining Break", 
                    f"{rb_h}h {rb_m}m",
                    # delta=f"{'-' if rb_h > 0 or rb_m > 0 else ''}{rb_h}h {rb_m}m",
                    # delta_color="inverse"
                )
            
            col1, col2 = st.columns(2)
        except Exception as e:
            st.error(f"An error occurred during calculation: {e}")

        with col1:
            st.metric(
                "Work Sessions", 
                str(len(result["sessions"])),
                help="Number of work sessions recorded"
            )
            st.subheader("Work Sessions")
            for i, s in enumerate(result["sessions"], 1):
                in_label = s["in"].strftime("%Y-%m-%d %H:%M")
                out_label = ("ONGOING (now " + s["out"].strftime("%Y-%m-%d %H:%M") + ")") if s["ongoing"] else s["out"].strftime("%Y-%m-%d %H:%M")
                mins = s["seconds"] // 60
                h, m = divmod(mins, 60)
                dur = f"{h}h {m}m" if h else f"{m}m"
                st.write(f"**Session {i}:** {in_label} → {out_label} = **{dur}**")

        with col2:
            st.metric(
                "Break Sessions", 
                str(len(result["breaks"])),
                help="Number of break sessions recorded"
            )
            st.subheader("Break Sessions")
            if result["breaks"]:
                for i, b in enumerate(result["breaks"], 1):
                    start_label = b["start"].strftime("%Y-%m-%d %H:%M")
                    end_label = b["end"].strftime("%Y-%m-%d %H:%M")
                    mins = b["seconds"] // 60
                    h, m = divmod(mins, 60)
                    dur = f"{h}h {m}m" if h else f"{m}m"
                    st.write(f"**Break {i}:** {start_label} → {end_label} = **{dur}**")
            else:
                st.info("No breaks detected.")
    
if __name__ == "__main__":
    main()
