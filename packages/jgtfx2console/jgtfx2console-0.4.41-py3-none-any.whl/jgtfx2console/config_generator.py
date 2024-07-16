import argparse


import os
import xml.etree.ElementTree as ET

def generate_config(instruments, timeframes, nb_bar=500, default_headers="DateTime,Bid Open,Bid Close,Ask High,Ask Low,Volume", data_dir=None,dt_sep=' ',tz_default='UTC'):
  # Split the CSV strings into lists
  instruments = instruments.split(',')
  timeframes = timeframes.split(',')

  if dt_sep == '' or dt_sep == 'space' or dt_sep == '0':
    dt_sep = ' '
  
  if dt_sep == 'tab':
    dt_sep = ' '
  

  # Create the root element
  config = ET.Element('configuration')

  # Create the Settings element
  settings = ET.SubElement(config, 'Settings')

  # Add the Login, OutputDir, and Url elements
  ET.SubElement(settings, 'Login').text = '0'#os.getenv('user_id','0')
  ET.SubElement(settings, 'OutputDir').text = data_dir or os.getenv('JGTPY_DATA')
  ET.SubElement(settings, 'Url').text = os.getenv('url','https://www.fxcorporate.com/Hosts.jsp')

  # Add the other elements
  ET.SubElement(settings, 'Connection').text = os.getenv('connection','Real')
  ET.SubElement(settings, 'SessionID').text = ''
  ET.SubElement(settings, 'Pin').text = ''
  ET.SubElement(settings, 'Delimiter').text = ','
  ET.SubElement(settings, 'DateTimeSeparator').text = dt_sep
  ET.SubElement(settings, 'FormatDecimalPlaces').text = 'Y'
  ET.SubElement(settings, 'Timezone').text = 'UTC'

  # Add the History elements
  for instrument in instruments:
    for timeframe in timeframes:
      history = ET.SubElement(settings, 'History')
      ET.SubElement(history, 'Instrument').text = instrument
      ET.SubElement(history, 'Timeframe').text = timeframe
      ifn = instrument.replace("/","-")
      ET.SubElement(history, 'Filename').text = f'{ifn}_{timeframe}.csv'
      ET.SubElement(history, 'NumBars').text = str(nb_bar)
      ET.SubElement(history, 'Headers').text = default_headers

  # Return the XML as a string
  return ET.tostring(config, encoding='utf8', method='xml').decode()

def main():
  import argparse
  parser = argparse.ArgumentParser(description='Generate a configuration file for the ptoLiveChartDataExport')
  parser.add_argument('-i','--instruments', help='The list of instruments to export (comma-separated)', required=True)
  parser.add_argument('-t','--timeframes', help='The list of timeframes to export (comma-separated)', required=True)
  parser.add_argument('-o','--outxml', type=str,default="fxliveconfig.xml", help='Output XML file')

  #data_dir = os.getenv('JGTPY_DATA') or if --data_dir
  parser.add_argument('-d','--data_dir', help='The directory where the data will be saved')
  


  args = parser.parse_args()
  instruments = args.instruments
  timeframes = args.timeframes
  data_dir =  args.data_dir or os.getenv('JGTPY_DATA')
  outxml = args.outxml

  # Generate the configuration
  config = generate_config(instruments, timeframes, data_dir=data_dir)

  # Print the configuration
  print(config)
  with open(outxml, 'w') as f:
    f.write(config)
    print("Configuration file written to:", outxml)

if __name__ == '__main__':
  main()