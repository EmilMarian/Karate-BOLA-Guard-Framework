package karate;

import net.masterthought.cucumber.Configuration;
import net.masterthought.cucumber.ReportBuilder;
import net.masterthought.cucumber.json.support.Status;


import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class CucumberReportGenerator {

    public static void main(String[] args) {
        File reportOutputDirectory = new File("target/karate-reports");
        List<String> jsonFiles = new ArrayList<>();
        jsonFiles.add("target/karate-reports"); // path to the Karate JSON output

        String buildNumber = "1";
        String projectName = "KarateTestRunner";


        Configuration configuration = new Configuration(reportOutputDirectory, projectName);
        configuration.setBuildNumber(buildNumber);
        configuration.addClassifications("Platform", System.getProperty("os.name"));
        configuration.addClassifications("Branch", "release/1.0");
//        configuration.setPresentationModes(PresentationMode.RUN_WITH_JENKINS);
//        configuration.setQualifierStatus("someQualifier", Status.PASSED);


        ReportBuilder reportBuilder = new ReportBuilder(jsonFiles, configuration);
        reportBuilder.generateReports();
    }
}
