package NetsManager;

import net.sf.saxon.Configuration;
import net.sf.saxon.Controller;
import net.sf.saxon.instruct.UserFunction;

import net.sf.saxon.om.*;
import net.sf.saxon.query.*;

import net.sf.saxon.value.IntegerValue;
import net.sf.saxon.value.Value;

import net.sf.saxon.xpath.*;

import javax.xml.transform.*;
import javax.xml.transform.stream.*;

import java.io.*;

import java.util.Properties;


public class Query {

	public static ByteArrayOutputStream qtabby;
	
	public boolean txty;

	public Query(InputStream f, String _query){
		txty = true;
	try{
		QRes(f, _query, null, false, false);
	}catch(Exception ee){System.out.println(ee.getMessage());}
	}

	public Query(InputStream f, String _query, String _parameter, boolean isfile){
	try{
		QRes(f, _query, _parameter, isfile, false);
	}catch(Exception ee){System.out.println(ee.getMessage());}
	}

	public Query(String _in, String _query, String _parameter, boolean isfile, boolean isxml){
	try{
		QRes(_in, _query, _parameter, isfile, isxml);
	}catch(Exception ee){System.out.println(ee.getMessage());}
	}

	public Query(String _in, String _query, String _parameter, boolean isfile){
		this(_in, _query, _parameter, isfile, false);
	}


 void QRes(String inn, String query, String parameter, boolean isfile, boolean isxml) 
								throws Exception {	
	try{
		QRes(new ByteArrayInputStream(inn.getBytes()), query, parameter, isfile, isxml);		
	}catch(Exception ee){System.out.println(ee.getMessage());}
		}


	   void QRes(InputStream in, String query, String parameter, boolean isFile, boolean isxml) 
										throws Exception {	

	        final Configuration config = new Configuration();
	        final StaticQueryContext sqc = new StaticQueryContext(config);

	        		 XQueryExpression exp;

	if(!isFile){
			 exp = sqc.compileQuery(query);
			 System.out.println("Using QueryLine");
		} else {
			 exp = 	sqc.compileQuery(
			new InputStreamReader(
			ClassLoader.getSystemResourceAsStream(query)));
			System.out.println("Query: "+query);
		}

	        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
	
		if(parameter !=null) dynamicContext.setParameter("value", parameter);
	        
	        dynamicContext.setContextNode(sqc.buildDocument(new StreamSource(in)));

	        final Properties props = new Properties();

	                                  props.setProperty(OutputKeys.ENCODING,"UTF-8");

	        if(txty) {
				props.setProperty(OutputKeys.METHOD, "text");
		         } else if (isxml){
				props.setProperty(OutputKeys.METHOD, "xml");
		         } else {
		   	            props.setProperty(OutputKeys.INDENT, "yes");
				props.setProperty(OutputKeys.METHOD, "html");
		         }

			 qtabby = new ByteArrayOutputStream();

	try{

		            exp.run(dynamicContext, new StreamResult(qtabby), props);

	}catch (Exception ee){ 
			qtabby.write(new String("Error in "+query).getBytes());
			return;
			}		
	}

     }
