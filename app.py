# app.py
import streamlit as st
from calculator import calculate_office_time
from datetime import datetime

def main():
    st.set_page_config(
        page_title="Time Calculator", 
        page_icon="⏰",
        layout="wide"
    )
    
    st.title("⏰ Time Calculator")
    st.markdown("Paste your biometric log data below to calculate work and break times.")
    
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
            # Use fixed Asia/Kolkata timezone
            result = calculate_office_time(raw_text, 'Asia/Kolkata')
            
            # Summary metrics in columns - now with 5 columns
            col_summary1, col_summary2, col_summary3, col_summary4, col_summary5 = st.columns(5)
            
            with col_summary1:
                st.metric(
                    "Total Work Time", 
                    f"{result['work_hours']}h {result['work_minutes']}m",
                    help="Target: 7h 30m"
                )
            
            with col_summary2:
                st.metric(
                    "Total Break Time", 
                    f"{result['break_hours']}h {result['break_minutes']}m",
                    help="Target: 1h 30m"
                )
            
            with col_summary3:
                st.metric(
                    "Total Time", 
                    f"{result['total_time_hours']}h {result['total_time_minutes']}m",
                    help="Work Time + Break Time"
                )
            
            rw_h, rw_m = result["remaining_work"]
            rb_h, rb_m = result["remaining_break"]
            
            with col_summary4:
                st.metric(
                    "Remaining Work", 
                    f"{rw_h}h {rw_m}m",
                )
            
            with col_summary5:
                st.metric(
                    "Remaining Break", 
                    f"{rb_h}h {rb_m}m",
                )
            
            # Session details in two columns
            col1, col2 = st.columns(2)

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
                
        except Exception as e:
            st.error(f"Error processing the input: {str(e)}")
    
   
if __name__ == "__main__":
    main()
