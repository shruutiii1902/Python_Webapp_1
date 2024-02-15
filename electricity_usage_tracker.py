import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
def load_df():
    df = pd.read_csv('electricity_bill_dataset.csv')
    return df

df = load_df()

# Title
st.title("Indian Household Electricity Consumption Dashboard")
#Divider
st.divider()
tab1,tab2=st.tabs(["Explore Data","Evaluations"])
with tab1:
    # Sidebar
    with st.sidebar.expander("**Description**"):
        st.write("The **Indian Household Electricity Consumption Dataset** is a comprehensive dataset that captures the electricity consumption patterns of Indian households. It includes information about the number of hours each household appliance, operates in a month. Additionally, it incorporates demographic factors like the city of residence and the electricity distribution company serving that city.")
    
    with st.sidebar.expander("**Intuition**"):
        st.write("Explore the dataset and visualize electricity consumption trends.")

    # Display raw data
    st.sidebar.subheader("Data")
    button_clicked = st.sidebar.button("Show Raw Data")
    if button_clicked:
        st.write(df)

    # Data Exploration
    st.sidebar.subheader('Data Exploration')
    option1 = st.sidebar.checkbox("Summary Statistics")
    summary_stats = df.describe()
    option2 = st.sidebar.checkbox("Viaualizations")
    if option1:
        st.write(summary_stats)
    if option2:
        #Brgrph to detect missing values
        st.subheader('Missing Values Detection Graph')
        msno.bar(df)
        plt.savefig("missing_values_plot.png")  # Save the plot as an image
        st.image("missing_values_plot.png")

        
        
        #Barplot to see top cities surveyed    
        top_cities = df['City'].value_counts().reset_index()
        top_cities.columns = ['City', 'Count']
        fig = px.bar(top_cities, x='City', y='Count', title='Top Cities surveyed')
        fig.update_layout(
            xaxis=dict(title='City'),
            yaxis=dict(title='Count'),
            xaxis_tickangle=-45,
            width=800,
            height=500
         )
        st.plotly_chart(fig)

        #Barplot to analyse tariffRate citiwise
        fig = px.bar(df, x='City', y='TariffRate', title='Tariff by City')
        fig.update_layout(
            xaxis=dict(title='City', tickangle=75),
            yaxis=dict(title='TariffRate'),
            width=800,
            height=500
        )
        st.plotly_chart(fig)
   
        
        
        #Multiple Barplot to analyse monthly Electricity Bill
        monthly_analysis = df.groupby('Month')['ElectricityBill'].agg(['min', 'max', 'mean'])
        plt.figure(figsize=(10,6))
        monthly_analysis.plot(kind='bar')
        plt.title('Monthly electricity bill analysis')
        fig = plt.gcf()
        st.pyplot(fig)

        
        #Multiple Barplot to visualize Citiwise appliance usage
        by_city=df.groupby('City').sum()
        dropped_df=by_city.drop(['MonthlyHours','TariffRate','ElectricityBill','Month'],axis=1)
        dropped_df.groupby('City').sum().plot(kind='bar')
        plt.title('Citiwise appliance usage')
        fig=plt.gcf()
        st.pyplot(fig)
    
        #Multiple Barplot to visualize Citiwise Electricity bill usage
        bill_insights=df.groupby('City').ElectricityBill.agg(['min','max','mean']).plot(kind='bar')
        plt.title('Citiwise Electricity bill usage')
        fig=plt.gcf()
        st.pyplot(fig)

        #Horizontal Barplot to show Top 5 Most Common Companies
        x=df[['City','Company']]
        top_companies = x.value_counts().nlargest(5)
        fig = go.Figure(go.Bar(
            y=top_companies.index.map(lambda x: f'{x[0]} - {x[1]}'),  # Combine 'City' and 'Company' for labels
            x=top_companies.values,
            orientation='h'
        ))
        fig.update_layout(
            title='Top 5 Most Common Companies',
            xaxis=dict(title='Count'),
            yaxis=dict(title='City - Company')
        )
        st.plotly_chart(fig)
      
        #Piechart to analyse Distribution of Monthly Hours by Appliance
        by_hrs=df.groupby('MonthlyHours').sum()
        drop_df=by_hrs.drop(['Month','City','Company','TariffRate','ElectricityBill'],axis=1)
        labels = drop_df.columns
        values = drop_df.sum()
        fig = go.Figure(go.Pie(labels=labels, values=values))
        fig.update_layout(title='Distribution of Monthly Hours by Appliance')
        st.plotly_chart(fig)


        #Barplot to see Hourly Electricity Consumption in a Month
        fig = px.bar(
            df,
            x="Month",
            y="MonthlyHours",
            color="MonthlyHours",
            title= "Hourly Electricity Consumption in a Month",
            color_continuous_scale="reds",
        )
        st.plotly_chart(fig, theme=None, use_container_width=True)

        #Correlation Heatmap
        df1=df.drop(['City','Company'],axis=1)
        correlation_matrix = df1.corr()
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='Viridis')
        )
        fig.update_layout(
            title='Correlation Heatmap',
            xaxis=dict(title='Features'),
            yaxis=dict(title='Features')
        )
        st.plotly_chart(fig)

with tab2:
    #Brplot for Fluctuaation in ElectricityBill with respect to usage of Appliances
    df2=df.drop(columns=['Month','City','Company','MonthlyHours','TariffRate'])
    def calculate_bill(df2):
        total_usage = df2['Fan'] + df2['Refrigerator'] + df2['Television'] + df2['AirConditioner'] + df2['Monitor']
        bill = total_usage * 0.1  # Assuming a rate of 0.1 units per appliance per hour
        df2['ElectricityBill'] = bill
        return df2

    st.subheader('Electricity Bill Calculator')
    

    selected_appliance = st.sidebar.selectbox("Select Appliance", df2.columns[:-1])
    usage = st.sidebar.slider(f'{selected_appliance.capitalize()} Usage (Hours)', min_value=0, max_value=24, value=0)
    df2[selected_appliance] = usage
    

    df2 = calculate_bill(df2)
    bill_by_appliance = df2.drop(columns=['ElectricityBill']).mean() * 0.1

    col1,col2=st.columns(2)
    with col1:
        # Create a bar graph for electricity bill
        fig, ax = plt.subplots()
        ax.bar(bill_by_appliance.index, bill_by_appliance)
        ax.set_xlabel('Appliance')
        ax.set_ylabel('Electricity Bill (USD)')
        ax.set_title('Electricity Bill by Appliance')
        st.pyplot(fig)

    with col2:
        st.write(bill_by_appliance)

    st.divider()


    #Barplot for Energy Usage over Time
    by_bill=df.groupby('ElectricityBill').sum()
    dropp_df=by_bill.drop(columns=['Fan','Refrigerator','AirConditioner','Television','Monitor','City','Company',])
    start_month = st.sidebar.number_input("Start Month", min_value=df["Month"].min(), max_value=df["Month"].max())
    end_month = st.sidebar.number_input("End Month", min_value=df["Month"].min(), max_value=df["Month"].max())
    filtered_df = df[(df["Month"] >= start_month) & (df["Month"] <= end_month)]
    #st.write(filtered_df)
    fig = px.bar(filtered_df, x="Month", y="ElectricityBill", title="Energy Usage Over Time")
    st.plotly_chart(fig)

    with st.sidebar.expander("**Insights**"):
        st.write('i.Energy Management')
        st.write('ii.Consumer Insights')

    
    st.markdown("---")
    st.markdown("Created with Streamlit")

    

    