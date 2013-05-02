/* Written by: Xiao-Long Chen <chenxiaolong@cxl.epac.to> */

/* This is the fglrx version of my hybrid-detect script */

/* Uses some code written by Canonical (see the hybrid-detect source code
 * in their nvidia-common package */

#include <pciaccess.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/utsname.h>
#include <unistd.h>

#define PCI_CLASS_DISPLAY 0x03

#define FILENAME "/var/lib/hybrid-detect/last_gfx_boot"

static struct pci_slot_match match = {
  PCI_MATCH_ANY, PCI_MATCH_ANY, PCI_MATCH_ANY, PCI_MATCH_ANY, 0
};

enum DRIVERS {
  INTEL,
  FGLRX
};

enum DRIVERS hybrid_mode;
static int      main_vendor_id = 0;
static int last_main_vendor_id = 0;
static int      main_device_id = 0;
static int last_main_device_id = 0;

void get_devices() {
  pci_system_init();

  struct pci_device_iterator *iterator = pci_slot_match_iterator_create(&match);

  if (iterator == NULL) {
    exit(1);
  }

  int intel_device_count = 0;
  int amd_device_count = 0;
  int found_main_gfx = 0;

  struct pci_device *info;
  while ((info = pci_device_next(iterator)) != NULL) {
    if ((info->device_class & 0x00ff0000) == (PCI_CLASS_DISPLAY << 16)) {
      if (pci_device_is_boot_vga(info) && found_main_gfx == 0) {
        if (info->vendor_id == 0x1002) {
          hybrid_mode = FGLRX;
        }
        else if (info->vendor_id == 0x8086) {
          hybrid_mode = INTEL;
        }
        else {
          fprintf(stderr, "Unknown graphics card: %x:%x\n",
                  info->vendor_id, info->device_id);
          exit(1);
        }

        found_main_gfx = 1;
        main_vendor_id = info->vendor_id;
        main_device_id = info->device_id;
      }

      /* Use two counters since some cards, like the GMA4500MHD, have 2 PCI
       * IDs: the display controller and the actual graphics card */
      if (info->vendor_id == 0x1002) {
        amd_device_count++;
      }
      else if (info->vendor_id == 0x8086) {
        intel_device_count++;
      }
    }
  }

  /* If there's more than one graphics card, warn the user and exit. This only
   * systems with muxes (ie. no AMD Enduro) */
  if (intel_device_count > 0 && amd_device_count > 0) {
    fprintf(stderr, "%i AMD graphics card(s) and %i Intel graphics card(s) detected: AMD Enduro system? Exiting...\n", 
            amd_device_count, intel_device_count);
    exit(1);
  }
}

void last_boot_gfx() {
  FILE *fptr = NULL;

  fptr = fopen(FILENAME, "r");

  if (fptr == NULL) {
    fprintf(stderr, "Couldn't read from %s\n", FILENAME);

    /* If file doesn't exist, then create it */
    fprintf(stdout, "Creating %s\n", FILENAME);
    fptr = fopen(FILENAME, "w");

    if (fptr == NULL) {
      fprintf(stderr, "Could not write to %s\n", FILENAME);
      exit(1);
    }

    /* Write vendor and device IDs and then continue */
    fprintf(fptr, "%x:%x\n", 0x00, 0x00);
    fflush(fptr);
    fclose(fptr);
    fptr = fopen(FILENAME, "r");
  }

  fscanf(fptr, "%x:%x\n", &last_main_vendor_id, &last_main_device_id);
  fclose(fptr);
}

void write_ids() {
  if (last_main_vendor_id != main_vendor_id) {
    FILE *fptr;

    fptr = fopen(FILENAME, "w");

    if (fptr == NULL) {
      fprintf(stderr, "Could not write to %s\n", FILENAME);
      exit(1);
    }

    fprintf(fptr, "%x:%x\n", main_vendor_id, main_device_id);
    fflush(fptr);
    fclose(fptr);
  }
}

void update_alternatives() {
  if (last_main_vendor_id == 0 ||
      last_main_vendor_id != main_vendor_id) {
    fprintf(stdout, "Hybrid graphics mode was changed in the BIOS\n");
  }

  struct utsname uts;
  if (uname(&uts) < 0) {
    fprintf(stderr, "Failed to detect CPU architecture\n");
    exit(1);
  }

  switch (hybrid_mode) {
  case INTEL:
    system("update-alternatives --set 00-gfx.conf /etc/X11/modulepath.intel.conf");

    if (strcmp(uts.machine, "x86_64") == 0) {
      system("update-alternatives --set fglrx-lib64.conf /dev/null");
    }
    system("update-alternatives --set fglrx-lib.conf /dev/null");
    break;
  case FGLRX:
    system("update-alternatives --set 00-gfx.conf /etc/X11/modulepath.fglrx.conf");
    if (strcmp(uts.machine, "x86_64") == 0) {
      if (access("/usr/share/fglrx/fglrx-lib.conf", F_OK) == 0) {
        /* Multilib fglrx libraries are installed */
        system("update-alternatives --set fglrx-lib.conf /usr/share/fglrx/fglrx-lib.conf");
      }
      system("update-alternatives --set fglrx-lib64.conf /usr/share/fglrx/fglrx-lib64.conf");
    }
    else {
      system("update-alternatives --set fglrx-lib.conf /usr/share/fglrx/fglrx-lib.conf");
    }
    break;
  }
}

int main(int argc, char *argv[]) {
  /* Must be run as root */
  if (getuid() != 0) {
    fprintf(stderr, "%s must be run as root\n", argv[0]);
    exit(1);
  }

  last_boot_gfx();
  get_devices();
  write_ids();
  update_alternatives();

  system("LDCONFIG_NOTRIGGER=y ldconfig");
}
