.. ByteBlower Test Framework documentation master file for inclusion
   in the ByteBlower Test Framework overview documentation.
   You can adapt this file completely to your liking, but it should at least
   contain the root ``toctree`` directive.

Welcome to ByteBlower Test Framework's documentation!
=====================================================

The ByteBlower Test Framework is everything you need for automating traffic
tests! Starting from traffic test definition, over traffic generation and
analysis, to reporting and validating according to your KPIs!

.. grid:: 12
   :gutter: 2

   .. grid-item-card:: Highlights
      :columns: 12
      :text-align: center

      What are the benefits of using this new approach to traffic test automation?

   .. grid-item-card:: KPI analysis
      :columns: 4
      :margin: 4 2 auto auto
      :img-bottom: images/overview/kpi_summary.png
      :img-alt: KPI analysis summary
      :text-align: left

      Key performance indicator (KPI) metrics are analyzed automatically
      and summarized in the report.
      Possibility to specify your own thresholds.

   .. grid-item-card:: Failure causes
      :columns: 8
      :margin: 4 2 auto auto
      :img-top: images/overview/kpi_analysis.png
      :img-alt: KPI analysis failure causes
      :text-align: right

      Details included of the causes of failures of your KPI validation.

   .. grid-item-card:: Application specific KPIs
      :columns: 8
      :margin: 5 2 auto auto
      :img-bottom: images/overview/streaming_video_graph_over_time.png
      :img-alt: Streaming video buffer analysis graph over time
      :text-align: left

      Application simulations support you in validating your network for
      real-life traffic.

      For example: *A summary of analysis of the buffer of a streaming video
      test.*

   .. grid-item-card:: Application specific KPIs
      :columns: 4
      :margin: 5 2 auto auto
      :img-top: images/overview/streaming_video_buffer_summary.png
      :img-alt: Streaming video buffer analysis summary
      :text-align: right

      Also the application simulations have their own KPIs, ready for use.

   .. grid-item-card:: Application specific KPIs
      :columns: 4
      :margin: 2 2 auto auto
      :img-top: images/overview/voice_summary.png
      :img-alt: VoIP analysis summary
      :text-align: left

      Example: *Summary of the analysis of a VoIP test*

   .. grid-item-card:: Application specific KPIs
      :columns: 8
      :margin: 2 2 auto auto
      :img-top: images/overview/voice_graph_over_time.png
      :img-alt: VoIP analysis graph over time
      :text-align: right

      Detailed over-time analysis of a VoIP test

   .. grid-item-card:: Compare your results
      :columns: 12
      :margin: 5 2 auto auto
      :img-top: images/overview/compare_latency_ccdf.png
      :img-alt: Comparing Latency CCDF
      :text-align: center

      Easy comparison of test results

   .. grid-item-card:: Detailed analysis
      :columns: 12
      :margin: 5 2 auto auto
      :img-top: images/overview/tcp_graph_over_time.png
      :img-alt: TCP analysis graph over time
      :text-align: center

      Packed with important metrics to support detailed analysis.
      Starting from the KPI analysis, over the summary, to results over time

   .. grid-item-card:: Detailed analysis
      :columns: 12
      :margin: 2 2 auto auto
      :img-top: images/overview/latency_cdf.png
      :img-alt: Latency CDF
      :text-align: center

      Latency matters! The Latency CDF graph plots present the percentage
      of latency falling below a given threshold, offering a perspective
      on the overall latency distribution.

   .. grid-item-card:: Detailed analysis
      :columns: 12
      :margin: 2 2 auto auto
      :img-top: images/overview/latency_ccdf.png
      :img-alt: Latency CCDF
      :text-align: center

      Meanwhile, the Latency CCDF graph complements CDF by illustrating
      the latency distribution, to help you understanding the
      quality of service for time-sensitive applications.

.. toctree::
   :maxdepth: 1
   :caption: Contents

   overview
   quick_start
   examples/index

.. toctree::
   :maxdepth: 1
   :caption: Reference

   cli/index
   config/index
   reference
