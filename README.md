# Tech Mapping Dashboard Demo

This is a self-contained demo of the Tech Mapping Dashboard built with Streamlit. It includes sample data for immediate exploration—no file uploads required!

## Quick Start

1. **Install dependencies** (in a new virtual environment is recommended):
   ```sh
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```sh
   streamlit run app.py
   ```

3. **Explore:**
   - The dashboard will open in your browser.
   - By default, it loads the included demo data from the `demo_data/` folder.
   - This data has been preprocessed from bio- and e-fuels publications.

## Folder Structure

```
demo/
  app.py
  requirements.txt
  README.md
  demo_data/
    occurrence.csv
    cooccurrence.csv
    country.csv
    fact_alias_cluster.csv
```

- `app.py`: Main Streamlit dashboard.
- `demo_data/`: Contains all demo CSVs used by default.
- `requirements.txt`: All required Python packages.
- `README.md`: This file.

Enjoy exploring the Tech Mapping Dashboard!
